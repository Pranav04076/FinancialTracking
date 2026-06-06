from uuid import uuid4
import pandas as pd
from app.models import Transaction
from app.schemas import TransactionType
from sqlalchemy.orm import Session


REQUIRED_COLUMNS = {"type", "mode", "amount", "valuedate", "narration"}

def parse_csv(file_path: str, user_id, db: Session) -> tuple[int, int]:

    df = pd.read_csv(file_path, on_bad_lines="skip")
    df.columns = df.columns.str.strip().str.lower()

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df[["type", "mode", "amount", "valuedate", "narration", "txnid"]]

    df = df.dropna(subset=list(REQUIRED_COLUMNS))

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["amount"])
    df = df[df["amount"] > 0]

    df["valuedate"] = pd.to_datetime(df["valuedate"], errors="coerce").dt.date
    df = df.dropna(subset=["valuedate"])

    valid_types = {t.value for t in TransactionType}
    df = df[df["type"].str.upper().isin(valid_types)]

    existing_txnid = set(
    row[0] for row in
    db.query(Transaction.txn_id)
    .filter(Transaction.user_id == user_id)
    .all()
    )

    inserted = 0
    skipped = 0
    transactions = []
    for _, row in df.iterrows():
        txnid = str(row["txnid"]).strip() if pd.notna(row["txnid"]) else None

        # skip if txnId already exists in database
        if txnid and txnid in existing_txnid:
                skipped += 1
                continue

        tx_type = TransactionType(row["type"].upper())
        transaction = Transaction(
            id=uuid4(),
            user_id=user_id,
            txn_id=txnid,
            type=tx_type,
            mode=str(row["mode"]).strip(),
            amount=float(row["amount"]),
            valueDate=row["valuedate"],
            narration=str(row["narration"]).strip()
        )
        transactions.append(transaction)
        inserted += 1


    db.bulk_save_objects(transactions)
    db.commit()

    return inserted, skipped


    
