from flask import Flask, request, jsonify
import logging
from src.classifier import classify_file, load_ml_model


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

ml_model = load_ml_model()

@app.route('/classify_file', methods=['POST'])
def classify_route():
    # Log the incoming request
    logging.info("Received classification request")

    # Check if file is present in request
    if 'file' not in request.files:
        logging.error("No file in request")
        return jsonify({
            "error": "No file provided",
            "message": "Please include a file in the request",
            "help": "Use -F 'file=@path_to_your_file' in your curl command"
        }), 400

    file = request.files['file']

    # Check if file was selected
    if file.filename == '':
        logging.error("No file selected")
        return jsonify({
            "error": "No file selected",
            "message": "Please select a file",
            "help": "Make sure your file path is correct"
        }), 400

    # Validate file extension
    if not allowed_file(file.filename):
        logging.error(f"Invalid file type: {file.filename}")
        return jsonify({
            "error": "Invalid file type",
            "message": f"Allowed file types are: {', '.join(ALLOWED_EXTENSIONS)}",
            "help": "Check your file extension and try again"
        }), 400

    # Classify the file
    result = classify_file(file, ml_model=ml_model)
    logging.info(f"Classification result for {file.filename}: {result}")
    return jsonify({
        "filename": file.filename,
        "classification": result["type"],
        "confidence": result["confidence"],
        "matched_keywords": result["matched_keywords"],
        "message": result["message"]
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)