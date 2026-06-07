import joblib

model = joblib.load("app/ML/model.pkl")

def predict_category(merchant: str):
    return model.predict([merchant])[0]