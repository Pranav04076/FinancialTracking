from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.models import Transaction
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import TransactionCreate, TransactionType, TransactionUpdate
from app.ML.predictor import predict_category

router = APIRouter(prefix = "/transactions", tags = ["transactions"])

@router.post("/create_transaction")
def createTransaction(
    transaction: TransactionCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_Transaction = Transaction(
        user_id = current_user.id,
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


@router.get("/get_Transactions")
def get_transactions(
                    limit: int = 10,
                    offset: int = 0,
                    db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    transactions = (db.query(Transaction).filter(Transaction.user_id==current_user.id).offset(offset).limit(limit).all())

    return transactions


@router.get("/balance") 
def get_balance(
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    


    credit = (
        db.query(func.sum(Transaction.amount))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.type == TransactionType.CREDIT
        )
        .scalar() or 0
    )

    debit = (
        db.query(func.sum(Transaction.amount))
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.type == TransactionType.DEBIT
        )
        .scalar() or 0
    )

    return {"balance": credit - debit}

@router.get("/get_transaction/{transaction_id}")
def get_transaction(transaction_id: UUID, 
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    transaction = (db.query(Transaction).filter(Transaction.id == transaction_id, 
                                                Transaction.user_id==current_user.id)).first()
    
    if transaction is None:
        raise HTTPException(status_code=401,detail = 'Transaction ID not found')
    
    return  {
    "id": transaction.id,
    "amount": transaction.amount,
    "mode": transaction.mode,
    "type": transaction.type.value,
    "narration": transaction.narration
}

@router.put("/update_transaction/{transaction_id}")
def update_transaction(transaction_id: UUID,
                       update_data: TransactionUpdate,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    
    transaction = (db.query(Transaction).filter(Transaction.id == transaction_id,
                                                Transaction.user_id==current_user.id)).first()
    
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

@router.delete("/delete_transaction/{transaction_id}")
def delete_transaction(transaction_id: UUID, 
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    transaction = (db.query(Transaction).filter(Transaction.id == transaction_id,
                                                Transaction.user_id == current_user.id)).first()
    
    if transaction is None:
        raise HTTPException(status_code=401, detail="Transaction not found")
    
    db.delete(transaction)
    db.commit()

    return {"message": "Deleted Successfully"}