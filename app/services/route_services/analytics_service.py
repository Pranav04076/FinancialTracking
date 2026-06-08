from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.models import Transaction
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import TransactionCreate, TransactionType, TransactionUpdate
from app.services.parsers.insights import gather_user_data, get_ai_insights, build_prompt
from datetime import datetime, date

def get_balance(db: Session,
                user_id: UUID):
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
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.DEBIT
            )
            .scalar() or 0
        )

    return {"balance": credit - debit}

def total_debit(db: Session,
                user_id: UUID):
    
    total_debit = (db.query(func.sum(Transaction.amount)).filter(Transaction.user_id==user_id.id, 
                                                                 Transaction.type == TransactionType.DEBIT)).scalar() or 0
    
    return {"total_debit": total_debit}

def total_credit(db: Session,
               user_id: UUID):
    
    total_credit = (db.query(func.sum(Transaction.amount)).filter(Transaction.user_id==user_id, 
                                                                 Transaction.type == TransactionType.CREDIT)).scalar() or 0
    
    return {"total_credit": total_credit}

def monthly_income(month: int,
                   year: int,
                   db: Session,
                  user_id: UUID):
    
    income = (db.query(func.sum(Transaction.amount)).filter(Transaction.user_id==user_id, 
                                                            Transaction.type==TransactionType.CREDIT,
                                                            func.extract("month", Transaction.valueDate)==month,
                                                            func.extract("year", Transaction.valueDate)==year
                                                            ).scalar() or 0)  
    
    if income is None:
        raise HTTPException(status_code=401, detail="No income found for this month")

    return {"month": month, 
            "year": year, 
            "monthly_income": income} 


def monthly_expense(month: int,
                   year: int,
                   db: Session,
                   user_id: UUID):
    
    expense = (db.query(func.sum(Transaction.amount)).filter(Transaction.user_id==user_id, 
                                                            Transaction.type==TransactionType.DEBIT,
                                                            func.extract("month", Transaction.valueDate)==month,
                                                            func.extract("year", Transaction.valueDate)==year
                                                            ).scalar() or 0)  
    if expense is None:
        raise HTTPException(status_code=401, detail="No expense found for this month")

    return {"month": month, 
            "year": year, 
            "monthly_expense": expense}

def monthly_net(month: int, 
                year: int,
                db: Session,
                user_id: UUID):
    
    income = (db.query(func.sum(Transaction.amount)).filter(Transaction.user_id==user_id, 
                                                            Transaction.type==TransactionType.CREDIT,
                                                            func.extract("month", Transaction.valueDate)==month,
                                                            func.extract("year", Transaction.valueDate)==year
                                                            ).scalar() or 0)  
    
    
    expense = (db.query(func.sum(Transaction.amount)).filter(Transaction.user_id==user_id, 
                                                            Transaction.type==TransactionType.DEBIT,
                                                            func.extract("month", Transaction.valueDate)==month,
                                                            func.extract("year", Transaction.valueDate)==year
                                                            ).scalar() or 0)
    
    balance = income - expense

    return {"month": month, "year": year,
            "income": income, "expense": expense,
            "total_monthly_net": balance}


def largest_expense(month: int, 
                year: int,
                db: Session,
                user_id: UUID):
    
    largest_expense = (db.query(Transaction).filter(Transaction.user_id==user_id, 
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

def largest_income(month: int, 
                year: int,
                db: Session,
                user_id: UUID):
    
    largest_income = (db.query(Transaction).filter(Transaction.user_id==user_id, 
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

def avg_transaction(month: int, 
                year: int,
                db: Session,
                user_id: UUID):
    
    avg_amount = (db.query(func.avg(Transaction.amount)).filter(Transaction.user_id==user_id, 
                                                            func.extract("month", Transaction.valueDate)==month,
                                                            func.extract("year", Transaction.valueDate)==year)
                                                            .scalar() or 0)
    

    return {"avg_transaction_amount": avg_amount}

def transactions_between(
    start_date: date,
    end_date: date,
    db: Session,
    user_id: UUID
):
    if start_date>end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after end date")
    
    transactions = (db.query(Transaction).filter(Transaction.user_id == user_id,
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


def get_monthly_savings(db: Session,
                        user_id: UUID,
                        month: int = datetime.now().month,
                        year: int = datetime.now().year
                        ):
    
    income = db.query(func.sum(Transaction.amount)).filter(Transaction.user_id==user_id,
                                          Transaction.type== TransactionType.CREDIT,
                                          extract("month", Transaction.valueDate)==month,
                                          extract("year", Transaction.valueDate)==year).scalar() or 0
    
    expense =  db.query(func.sum(Transaction.amount)).filter(Transaction.user_id==user_id,
                                          Transaction.type== TransactionType.DEBIT,
                                          extract("month", Transaction.valueDate)==month,
                                          extract("year", Transaction.valueDate)==year).scalar() or 0
    
    monthly_saving = income-expense
    savings_rate = round((monthly_saving/income)*100, 2)

    return {
        "month": month,
        "year": year,
        "income": income,
        "expense": expense,
        "savings": monthly_saving,
        "savings_rate": savings_rate
    }

def get_recent_transactions(db: Session,
                            user_id: UUID,
                            limit: int = 10,
                            ):
    
    transactions = db.query(Transaction).filter(Transaction.user_id==user_id).order_by(Transaction.valueDate.desc()).limit(limit).all()

    return [{
        "amount": t.amount,
        "type": t.type.value,
        "category": t.category,
        "narration": t.narration,
        "date": t.valueDate,
        "mode": t.mode
    }for t in transactions]

def category_breakdown(
    month: int,
    year: int,
    db: Session,
    user_id: UUID
):
    result = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == TransactionType.DEBIT,
        func.extract("month", Transaction.valueDate) == month,
        func.extract("year", Transaction.valueDate) == year
    ).group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).all()

    total_spent = sum(r.total for r in result)

    return [
        {
            "category": r.category,
            "amount": round(r.total, 2),
            "percentage": round((r.total / total_spent) * 100, 2) if total_spent > 0 else 0
        }
        for r in result
    ]


def spending_trends(
    year: int,
    db: Session,
    user_id: UUID
):
    result = db.query(
        func.extract("month", Transaction.valueDate).label("month"),
        func.sum(Transaction.amount).label("expense")
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == TransactionType.DEBIT,
        func.extract("year", Transaction.valueDate) == year
    ).group_by("month").order_by("month").all()

    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

    return [
        {
            "month": months[int(r.month) - 1],
            "month_number": int(r.month),
            "expense": round(r.expense, 2)
        }
        for r in result
    ]

def get_insights(db: Session,
                user_id: UUID,
                month: int= datetime.now().month,
                year: int = datetime.now().year
                ):
    
    data = gather_user_data(user_id, month, year, db)
    prompt = build_prompt(data, month, year)
    insights = get_ai_insights(prompt)


    return {
        "month": month,
        "year": year,
        "inights": insights
    }