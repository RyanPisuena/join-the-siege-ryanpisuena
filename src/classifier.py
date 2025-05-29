from werkzeug.datastructures import FileStorage
import PyPDF2
import pytesseract
from PIL import Image
import io
from difflib import get_close_matches
import logging
import joblib
import os

# Define document types and their associated keywords
DOCUMENT_TYPES = {
    'drivers_licence': [
        'license', 'licence', 'identification', 'class', 'dob', 'weight', 'height',
        'driver', 'operator', 'permit', 'expires', 'restrictions', 'endorsements',
        'state', 'sex', 'eyes', 'signature', 'issued', 'birth', 'expiration',
        'commercial', 'non-commercial', 'id number', 'dl number', 'driving'
    ],
    'bank_statement': [
        'statement', 'balance', 'account', 'transaction', 'deposit', 'withdrawal',
        'bank', 'checking', 'savings', 'beginning balance', 'ending balance'
    ],
    'invoice': [
        'invoice', 'bill to', 'amount due', 'payment', 'details', 'total',
        'subtotal', 'tax', 'due date', 'invoice number', 'order number'
    ]
}

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'model.pkl')

def classify_by_ml(content_text: str) -> dict:
    """Classify using the ML model. Returns result dict or None if not confident or fails."""
    try:
        model = joblib.load(MODEL_PATH)
        pred = model.predict([content_text])[0]
        proba = max(model.predict_proba([content_text])[0])
        if proba > 0.3:  # You can adjust this threshold
            return {
                "type": pred,
                "confidence": round(proba, 2),
                "matched_keywords": [],
                "message": "Classified by ML model"
            }
        else:
            logging.info(f"ML model prediction confidence too low: {proba} for input: {repr(content_text)[:200]}")
    except Exception as ml_error:
        logging.warning(f"ML model classification failed: {ml_error}")
    return None

def classify_by_ocr_keywords(content_text: str) -> dict:
    """Classify using OCR/keyword logic. Returns result dict or None if not confident or fails."""
    try:
        scores = {}
        matched_keywords = {}
        for doc_type, keywords in DOCUMENT_TYPES.items():
            score = calculate_document_score(content_text, keywords)
            matched = [k for k in keywords if k in content_text]
            scores[doc_type] = score
            matched_keywords[doc_type] = matched
        best_match = max(scores.items(), key=lambda x: x[1])
        doc_type, confidence = best_match
        if confidence >= 0.1:
            return {
                "type": doc_type,
                "confidence": round(confidence, 2),
                "matched_keywords": matched_keywords[doc_type],
                "message": "Classified by OCR/keywords"
            }
    except Exception as ocr_error:
        logging.warning(f"OCR/keyword classification failed: {ocr_error}")
    return None

def get_text_from_file(file: FileStorage) -> str:
    """Extract text from different file types with error handling"""
    try:
        filename = file.filename.lower()
        if filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(file.stream)
            text = ' '.join(page.extract_text() for page in pdf_reader.pages)
            logging.info(f"Successfully extracted text from PDF: {filename}")

        elif filename.endswith(('.jpg', '.jpeg', '.png')):
            try:
                image = Image.open(file.stream)
                logging.info(f"Successfully opened image: {filename}")
                
                # Try to improve image quality for OCR
                image = image.convert('L')  # Convert to grayscale
                logging.info("Converted image to grayscale")
                
                # Configure tesseract for better accuracy
                custom_config = r'--oem 3 --psm 6'
                text = pytesseract.image_to_string(image, config=custom_config)
                logging.info(f"Successfully extracted text from image using Tesseract")
                
                if not text.strip():
                    logging.warning(f"No text extracted from image: {filename}")
                    text = "NO_TEXT_EXTRACTED"
                
            except Exception as img_error:
                logging.error(f"Error processing image {filename}: {str(img_error)}")
                raise
            
        else:
            raise ValueError(f"Unsupported file type: {filename}")
        
        # Reset file stream for potential reuse
        file.stream.seek(0)
        return text.lower()
    except Exception as e:
        logging.error(f"Error extracting text from file {file.filename}: {str(e)}")
        raise

def calculate_document_score(text: str, keywords: list) -> float:
    """Calculate how well the text matches a document type's keywords"""
    if text == "NO_TEXT_EXTRACTED":
        return 0.0
        
    text = text.lower()
    # Count both exact matches and partial matches
    exact_matches = sum(1 for keyword in keywords if keyword in text)
    partial_matches = sum(1 for keyword in keywords if any(word in keyword for word in text.split()))
    
    # Weight exact matches more heavily
    score = (exact_matches * 1.0 + partial_matches * 0.5) / len(keywords)
    return score

def classify_by_filename(filename: str) -> str:
    filename = filename.lower()
    if "drivers_license" in filename or "drivers_licence" in filename:
        return "drivers_licence"
    if "bank_statement" in filename:
        return "bank_statement"
    if "invoice" in filename:
        return "invoice"
    return "unknown"

def classify_file(file: FileStorage) -> dict:
    try:
        content_text = get_text_from_file(file)
    except Exception as e:
        logging.error(f"Error extracting text from file: {e}")
        # Fallback to filename if text extraction fails
        try:
            fallback_type = classify_by_filename(file.filename)
            return {
                "type": fallback_type,
                "confidence": 0,
                "matched_keywords": [],
                "message": f"Text extraction failed, classified by filename fallback: {str(e)}"
            }
        except Exception as fallback_error:
            return {
                "type": "unknown",
                "confidence": 0,
                "matched_keywords": [],
                "message": f"ML, text extraction and filename classification failed: {str(fallback_error)}"
            }

    # 1. Try ML model
    ml_result = classify_by_ml(content_text)
    if ml_result:
        return ml_result

    # 2. Try OCR/keyword logic
    ocr_result = classify_by_ocr_keywords(content_text)
    if ocr_result:
        return ocr_result

    # 3. Fallback to filename
    try:
        fallback_type = classify_by_filename(file.filename)
        return {
            "type": fallback_type,
            "confidence": 0,
            "matched_keywords": [],
            "message": "Classified by filename fallback"
        }
    except Exception as fallback_error:
        return {
            "type": "unknown",
            "confidence": 0,
            "matched_keywords": [],
            "message": f"ML, content and filename classification failed: {str(fallback_error)}"
        }


