from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from fastapi import HTTPException
from app.models import Transaction
from app.schemas import TransactionCreate, TransactionUpdate, TransactionType
from app.ML.predictor import predict_category

def createTransaction(
    transaction: TransactionCreate, 
    db: Session,
    userid: UUID):
    new_Transaction = Transaction(
        user_id = userid,
        type = transaction.type,
        mode = transaction.mode,
        amount = transaction.amount,
        valueDate = transaction.valueDate,
        narration = transaction.narration,
        category = predict_category(transaction.narration)
    )

    db.add(new_Transaction)
    db.commit()
    db.refresh(new_Transaction)

    return new_Transaction

def get_transactions(
                    user_id: UUID,
                    db: Session,
                    limit: int = 10,
                    offset: int = 0,
                    ):
    
    transactions = (db.query(Transaction).filter(Transaction.user_id==user_id).offset(offset).limit(limit).all())

    return transactions

def get_balance(
                db: Session,
                user_id = UUID):
    


    credit = (
        db.query(func.sum(Transaction.amount))
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.CREDIT
        )
        .scalar() or 0
    )

    debit = (
        db.query(func.sum(Transaction.amount))
        .filter(
            Transaction.user_id == user_id.id,
            Transaction.type == TransactionType.DEBIT
        )
        .scalar() or 0
    )

    return {"balance": credit - debit}


def get_transaction_by_id(transaction_id: UUID, 
                    user_id: UUID,
                    db: Session
                    ):
    transaction = (db.query(Transaction).filter(Transaction.id == transaction_id, 
                                                Transaction.user_id==user_id)).first()
    
    if transaction is None:
        raise HTTPException(status_code=401,detail = 'Transaction ID not found')
    
    return  {
    "id": transaction.id,
    "amount": transaction.amount,
    "mode": transaction.mode,
    "type": transaction.type.value,
    "narration": transaction.narration
}

def update_transaction(transaction_id: UUID,
                       update_data: TransactionUpdate,
                       user_id: UUID,
                       db: Session
                       ):
    
    transaction = (db.query(Transaction).filter(Transaction.id == transaction_id,
                                                Transaction.user_id==user_id)).first()
    
    if transaction is None: 
        raise HTTPException(status_code=401, detail = 'Transaction ID not found')
    
    if update_data.amount is not None:
        transaction.amount = update_data.amount

    if update_data.mode is not None:
        transaction.mode = update_data.mode

    if update_data.narration is not None:
        transaction.narration = update_data.narration

    if update_data.valueDate is not None: 
        transaction.valueDate = update_data.valueDate

    if update_data.category is not None:
        transaction.category = update_data.category

    db.commit()
    db.refresh(transaction)

    return {
        "id": str(transaction.id),
        "amount": transaction.amount,
        "mode": transaction.mode,
        "type": transaction.type.value,
        "narration": transaction.narration,
        "valueDate": transaction.valueDate
    }

def delete_transaction(transaction_id: UUID, 
                       user_id: UUID,
                       db: Session
                       ):
    transaction = (db.query(Transaction).filter(Transaction.id == transaction_id,
                                                Transaction.user_id == UUID)).first()
    
    if transaction is None:
        raise HTTPException(status_code=401, detail="Transaction not found")
    
    db.delete(transaction)
    db.commit()

    return {"message": "Deleted Successfully"}