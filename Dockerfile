# Use an official Python image
FROM python:3.11-slim

# Install Tesseract and other system dependencies
RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev \
    poppler-utils gcc && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

# Expose the port your app runs on
EXPOSE 5001

# Set environment variables (optional, for Flask)
ENV FLASK_APP=src/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5001

# Run the app
CMD ["gunicorn", "-c", "gunicorn_config.py", "src.app:app"]