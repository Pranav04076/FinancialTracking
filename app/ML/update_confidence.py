from app.db import SessionLocal
from app.models import Transaction
from app.ML.predictor import predict_category


db = SessionLocal()


transactions = db.query(Transaction).filter(
    Transaction.confidence == None
).all()


for tx in transactions:

    text = f"{tx.narration}"

    prediction = predict_category(text)

    tx.category = prediction["category"]
    tx.confidence = prediction["confidence"]

    print(
        tx.narration,
        "->",
        tx.category,
        tx.confidence
    )


db.commit()

print("Updated successfully")