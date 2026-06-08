import pdfplumber
from uuid import uuid4
from datetime import datetime, date
from app.schemas import TransactionType
from app.models import Transaction
from app.services.parsers.helpers import get_mode, parse_date, extract_tables
from app.ML.predictor import predict_category


def parse_hdfc(file_path,user_id, db):
    
    rows = extract_tables(file_path)


    existing_txn_ids = {
        txn_id
        for (txn_id,) in db.query(Transaction.txn_id)
                            .filter(Transaction.user_id == user_id)
                            .all()
        }

    transactions = []
    skipped = 0
    
    for row in rows:
        if not row or len(row)<7: 
            continue

        #skip header row
        if row[0] and "DATE" in row[0].upper():
            continue

        try:
            txn_date = parse_date(row[0])
            value_date  = parse_date(row[3])
        except Exception:
            skipped+=1
            continue

        narration = row[1]
        txn_id = row[2]
        debit = row[4]
        credit = row[5]
        mode = get_mode(narration)

        if txn_id and txn_id in existing_txn_ids:
            skipped += 1
            continue

        debit = (debit or "").strip()
        credit = (credit or "").strip()
        
        if debit and debit!='-':
            tx_type = TransactionType.DEBIT 
            amount = float(debit.replace("DR", "").replace(",", "").strip())

        elif credit and credit!='-':
            tx_type = TransactionType.CREDIT
            amount = float(credit.replace("CR", "").replace(",","").strip())

        else: continue

        

        transaction = Transaction(
                        id=uuid4(),
                        user_id=user_id,
                        txn_id=txn_id,
                        type=tx_type,
                        amount=amount,
                        valueDate=value_date,
                        narration=narration,
                        mode= mode,
                        category = predict_category(narration)
            )
        
        transactions.append(transaction)
        if txn_id:
            existing_txn_ids.add(txn_id)

    db.bulk_save_objects(transactions)
    db.commit()
        
    return len(transactions), skipped