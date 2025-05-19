from werkzeug.datastructures import FileStorage
import PyPDF2
import pytesseract
from PIL import Image
import io
from difflib import get_close_matches
import logging

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

def classify_file(file: FileStorage) -> dict:
    """Classify document with confidence score and matched keywords"""
    try:
        content_text = get_text_from_file(file)
        logging.info(f"Extracted text length: {len(content_text)}")
        logging.info(f"First 100 chars of extracted text: {content_text[:100]}")
        
        # Calculate scores for each document type
        scores = {}
        matched_keywords = {}
        
        for doc_type, keywords in DOCUMENT_TYPES.items():
            score = calculate_document_score(content_text, keywords)
            matched = [k for k in keywords if k in content_text]
            scores[doc_type] = score
            matched_keywords[doc_type] = matched
            logging.info(f"Score for {doc_type}: {score}, matched keywords: {matched}")
        
        # Get the best match
        best_match = max(scores.items(), key=lambda x: x[1])
        doc_type, confidence = best_match
        
        # If confidence is too low, mark as unknown
        if confidence < 0.1:  # Threshold can be adjusted
            logging.warning(f"Low confidence score ({confidence}) for {file.filename}")
            return {
                "type": "unknown",
                "confidence": 0,
                "matched_keywords": [],
                "message": "Could not confidently classify document",
                "debug_info": {
                    "extracted_text_sample": content_text[:100],
                    "scores": scores
                }
            }
            
        return {
            "type": doc_type,
            "confidence": round(confidence, 2),
            "matched_keywords": matched_keywords[doc_type],
            "message": "Document classified successfully",
            "debug_info": {
                "scores": scores
            }
        }
        
    except Exception as e:
        logging.error(f"Classification error: {str(e)}")
        return {
            "type": "error",
            "confidence": 0,
            "matched_keywords": [],
            "message": str(e)
        }

'''
from werkzeug.datastructures import FileStorage

def classify_file(file: FileStorage):
    filename = file.filename.lower()
    # file_bytes = file.read()

    if "drivers_license" in filename:
        return "drivers_licence"

    if "bank_statement" in filename:
        return "bank_statement"

    if "invoice" in filename:
        return "invoice"

    return "unknown file"
'''
