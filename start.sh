#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Start Gunicorn with auto-reload
gunicorn --config gunicorn_config.py --reload "src.app:app" 