import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

# Ensure models directory exists
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, 'model.pkl')

# Get absolute path to data
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'synthetic_data.json')

# Load data
with open(DATA_PATH, 'r') as f:
    data = json.load(f)

texts = [text for text, label in data]
labels = [label for text, label in data]

# Train pipeline
model = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', LogisticRegression(max_iter=1000))
])
model.fit(texts, labels)

# Save model
joblib.dump(model, MODEL_PATH)
print(f"✅ Model trained and saved to {MODEL_PATH}")