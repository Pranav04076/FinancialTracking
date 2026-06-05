from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.models import Transaction
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import TransactionCreate, TransactionType, TransactionUpdate
from datetime import date


router = APIRouter(prefix = "/analytics", tags = ["analytics"])

@router.get("/balance/")
def get_balance(db: Session = Depends(get_db),
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

@router.get("/total_debit/")
def total_debit(db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    total_debit = (db.query(func.sum(Transaction.amount)).filter(Transaction.user_id==current_user.id, 
                                                                 Transaction.type == TransactionType.DEBIT)).scalar() or 0
    
    return {"total_debit": total_debit}

@router.get("/total_credit/")
def total_credit(db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    total_credit = (db.query(func.sum(Transaction.amount)).filter(Transaction.user_id==current_user.id, 
                                                                 Transaction.type == TransactionType.CREDIT)).scalar() or 0
    
    return {"total_credit": total_credit}


@router.get("/monthly_income/")
def monthly_income(month: int,
                   year: int,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    
    income = (db.query(func.sum(Transaction.amount)).filter(Transaction.user_id==current_user.id, 
                                                            Transaction.type==TransactionType.CREDIT,
                                                            func.extract("month", Transaction.valueDate)==month,
                                                            func.extract("year", Transaction.valueDate)==year
                                                            ).scalar() or 0)  
    
    if income is None:
        raise HTTPException(status_code=401, detail="No income found for this month")

    return {"month": month, 
            "year": year, 
            "monthly_income": income}                   


@router.get("/monthly_expense/")
def monthly_expense(month: int,
                   year: int,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    
    expense = (db.query(func.sum(Transaction.amount)).filter(Transaction.user_id==current_user.id, 
                                                            Transaction.type==TransactionType.DEBIT,
                                                            func.extract("month", Transaction.valueDate)==month,
                                                            func.extract("year", Transaction.valueDate)==year
                                                            ).scalar() or 0)  
    if expense is None:
        raise HTTPException(status_code=401, detail="No expense found for this month")

    return {"month": month, 
            "year": year, 
            "monthly_expense": expense}


@router.get("/monthly_net/")
def monthly_net(month: int, 
                year: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    income = (db.query(func.sum(Transaction.amount)).filter(Transaction.user_id==current_user.id, 
                                                            Transaction.type==TransactionType.CREDIT,
                                                            func.extract("month", Transaction.valueDate)==month,
                                                            func.extract("year", Transaction.valueDate)==year
                                                            ).scalar() or 0)  
    
    
    expense = (db.query(func.sum(Transaction.amount)).filter(Transaction.user_id==current_user.id, 
                                                            Transaction.type==TransactionType.DEBIT,
                                                            func.extract("month", Transaction.valueDate)==month,
                                                            func.extract("year", Transaction.valueDate)==year
                                                            ).scalar() or 0)
    
    balance = income - expense

    return {"month": month, "year": year,
            "income": income, "expense": expense,
            "total_monthly_net": balance}

@router.get("/largest_expense")
def largest_expense(month: int, 
                year: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    largest_expense = (db.query(Transaction).filter(Transaction.user_id==current_user.id, 
                                                            Transaction.type==TransactionType.DEBIT,
                                                            func.extract("month", Transaction.valueDate)==month,
                                                            func.extract("year", Transaction.valueDate)==year)
                                                            .order_by(Transaction.amount.desc()).first())
    
    if largest_expense is None:
        raise HTTPException(status_code=401, detail="No expense found for this month")
    
    return {
        "amount": largest_expense.amount,
        "narration": largest_expense.narration,
        "date": largest_expense.valueDate,
        "mode": largest_expense.mode
    }

@router.get("/largest_income")
def largest_income(month: int, 
                year: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    largest_income = (db.query(Transaction).filter(Transaction.user_id==current_user.id, 
                                                            Transaction.type==TransactionType.CREDIT,
                                                            func.extract("month", Transaction.valueDate)==month,
                                                            func.extract("year", Transaction.valueDate)==year)
                                                            .order_by(Transaction.amount.desc()).first())
    
    if largest_income is None:
        raise HTTPException(status_code=401, detail="No expense found for this month")
    
    return {
        "amount": largest_income.amount,
        "narration": largest_income.narration,
        "date": largest_income.valueDate,
        "mode": largest_income.mode
    }


@router.get("/avg_transaction_amount/")
def avg_transaction(month: int, 
                year: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    avg_amount = (db.query(func.avg(Transaction.amount)).filter(Transaction.user_id==current_user.id, 
                                                            func.extract("month", Transaction.valueDate)==month,
                                                            func.extract("year", Transaction.valueDate)==year)
                                                            .scalar() or 0)
    

    return {"avg_transaction_amount": avg_amount}

@router.get("/transactions-between/")
def transactions_between(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: User= Depends(get_current_user)
):
    if start_date>end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date")
    
    transactions = (db.query(Transaction).filter(Transaction.user_id == current_user.id,
                                                  Transaction.valueDate >= start_date,
                                                  Transaction.valueDate <= end_date).order_by(Transaction.valueDate.desc()).all())
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "total": len(transactions),
        "transactions": [
            {
                "id": str(t.id),
                "amount": t.amount,
                "type": t.type.value,
                "mode": t.mode,
                "narration": t.narration,
                "date": t.valueDate
            }
            for t in transactions
        ]
    }