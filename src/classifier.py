from werkzeug.datastructures import FileStorage
import PyPDF2
import pytesseract  # for images
from PIL import Image
import io

def classify_file(file: FileStorage):
    filename = file.filename.lower()
    content_text = ""
    
    # Extract text based on file type
    if filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file.stream)
        content_text = ' '.join(page.extract_text() for page in pdf_reader.pages)
    elif filename.endswith(('.jpg', '.jpeg', '.png')):
        # For images (like driver's licenses)
        image = Image.open(file.stream)
        content_text = pytesseract.image_to_string(image)
    
    # Now analyze the content instead of filename
    if any(keyword in content_text.lower() for keyword in ['license', 'identification', 'class', 'dob','weight','height']):
        return "drivers_licence"
    
    if any(keyword in content_text.lower() for keyword in ['statement', 'balance', 'account', 'transaction']):
        return "bank_statement"
    
    if any(keyword in content_text.lower() for keyword in ['invoice', 'bill to', 'amount due', 'payment', 'details']):
        return "invoice"
        
    return "unknown file"

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
