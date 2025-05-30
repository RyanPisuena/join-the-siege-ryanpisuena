# Heron File Classifier Challenge

## Overview

This project is a robust, production-ready document classifier designed to automate document processing workflows in financial services and beyond. It uses a hybrid approach:
- **ML model** (trained on synthetic data)
- **OCR/keyword matching**
- **Filename fallback**

The classifier is exposed as a Flask API and is fully containerized with Docker for easy deployment and scalability.

---

## Features
- Classifies PDF and image files (JPG, PNG) by content, OCR, or filename
- ML model loaded once at startup for high performance
- Synthetic data generation and training pipeline included
- Robust error handling and logging
- Dockerized for easy deployment
- Extensible and maintainable codebase
- CI/CD pipeline with GitHub Actions

---

## Marking Criteria
- **Functionality:** Works as expected, robust fallback logic
- **Scalability:** Model loaded once, modular, Dockerized
- **Maintainability:** Modular, clear, and well-structured
- **Creativity:** Fallback logic, synthetic data, hybrid approach
- **Testing:** Basic tests present, more coverage would be ideal
- **Deployment:** Dockerized, requirements pinned, .env used, model loaded once, CI/CD

---

## How to Run

### 1. Clone the repository
```bash
git clone https://github.com/RyanPisuena/join-the-siege-ryanpisuena
cd join-the-siege-ryanpisuena
```

### 2. Set up environment variables
Copy the example file and fill in your own values:
```bash
cp .env.example .env
# Edit .env as needed (especially SECRET_KEY and OPENAI_API_KEY if using synthetic data)
```

### 3. Install dependencies
#### With Docker (recommended)
```bash
docker build -t heron-classifier .
```
#### Or locally (for development)
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Install Tesseract (required for OCR)
brew install tesseract  # macOS
sudo apt-get install tesseract-ocr  # Ubuntu/Debian
```

### 4. Train the ML model (optional, if you want to retrain)
```bash
python src/generate_synthetic_data.py
python src/train_model.py
```

### 5. Run the Flask app
```bash
python -m src.app
```
or with docker
```bash
docker run -p 5001:5001 --env-file .env heron-classifier
```

### 6. Test the classifier using curl
```bash
curl -X POST -F 'file=@path_to_your_file.pdf' http://127.0.0.1:5001/classify_file
```

### 7. Run tests
```bash
pytest
```

### Troubleshooting
- If you get errors about Tesseract, make sure it is installed and available in your PATH.
- If you get errors about missing environment variables, check your `.env` file.

---

## Write-up: Approach, Decisions, and Reflections

### Approach
I built a robust, production-ready document classifier that combines multiple strategies—machine learning, OCR/keyword matching, and filename fallback—so the system is resilient to poorly named files and adaptable to new document types.

### Key Features & Decisions
- **Hybrid Classification:** ML model (TfidfVectorizer + LogisticRegression), OCR/keyword fallback, and filename fallback.
- **Synthetic Data Generation:** Script included for generating training data, making it easy to extend to new industries.
- **Production-Readiness:** Fully containerized, uses environment variables, and loads the ML model once at startup.
- **CI/CD Pipeline:** GitHub Actions workflow for tests and Docker build on every push/PR.
- **Maintainability:** Modular code, robust error handling, and logging.

### Time Spent
I spent more than the suggested 3 hours to demonstrate a production-ready, extensible solution and show my approach to real-world engineering challenges. If limited to 3 hours, I would have prioritized the hybrid classification logic and basic error handling.

### Next Steps
- Add more comprehensive tests (especially for ML/OCR logic)
- Look into polishing the security of the app:
    - Store files securely (use a secure, non-public directory and randomize filenames)
    - Add rate limiting to your API endpoints (e.g., Flask-Limiter)
- Extend support to more file types (e.g., Word, Excel)
- Add advanced monitoring and alerting

---

## Contact
If you get stuck, contact ryan.p@herondata.io for help (or just to say hi)!



