import joblib

model = joblib.load("app/ML/model.pkl")

import re

def clean_text(text):
    text = text.lower()

    text = re.sub(r'\d+', ' ', text)


    text = re.sub(r'[^a-z\s]', ' ', text)


    text = " ".join(text.split())

    return text

def predict_category(narration: str):
    text = clean_text(narration)
    probabilities = model.predict_proba([text])[0]
    best_index = probabilities.argmax()

    category = model.classes_[best_index]
    confidence = float(probabilities[best_index])

    if confidence < 0.1:
        category = "Other"

    return {"category": category, "confidence": confidence}