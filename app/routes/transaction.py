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
from app.services.route_services.transaction_service import (
createTransaction, get_transactions, get_transaction_by_id,
    update_transaction, delete_transaction, get_balance)



router = APIRouter(prefix = "/transactions", tags = ["transactions"])

@router.post("/create_transaction")
def createTransaction_route(
    transaction: TransactionCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return createTransaction(transaction, db, current_user.id)


@router.get("/get_Transactions")
def get_transactions_route(
                    limit: int = 10,
                    offset: int = 0,
                    db: Session = Depends(get_db),
                     current_user: User = Depends(get_current_user)):
    return get_transactions(current_user.id, db, limit, offset)


@router.get("/balance") 
def get_balance_route(
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    return get_balance(db, current_user.id)

@router.get("/get_transaction/{transaction_id}")
def get_transaction_route(transaction_id: UUID, 
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    return get_transaction_by_id(transaction_id, current_user.id, db)

@router.put("/update_transaction/{transaction_id}")
def update_transaction_route(transaction_id: UUID,
                       update_data: TransactionUpdate,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    return update_transaction(transaction_id, update_data, current_user.id, db)
    

@router.delete("/delete_transaction/{transaction_id}")
def delete_transaction_route(transaction_id: UUID, 
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    return delete_transaction(transaction_id, current_user.id, db)