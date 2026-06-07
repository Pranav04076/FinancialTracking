from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.models import Transaction
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import TransactionCreate, TransactionType, TransactionUpdate
from app.services.insights import gather_user_data, get_ai_insights, build_prompt
from datetime import datetime, date


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

@router.get("/monthly_savings")
def get_monthly_savings(month: int = datetime.now().month,
                        year: int = datetime.now().year,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    
    income = db.query(func.sum(Transaction.amount)).filter(Transaction.user_id==current_user.id,
                                          Transaction.type== TransactionType.CREDIT,
                                          extract("month", Transaction.valueDate)==month,
                                          extract("year", Transaction.valueDate)==year).scalar() or 0
    
    expense =  db.query(func.sum(Transaction.amount)).filter(Transaction.user_id==current_user.id,
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

@router.get("/recent_transactions")
def get_recent_transactions(limit: int = 10,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    
    transactions = db.query(Transaction).filter(Transaction.user_id==current_user.id).order_by(Transaction.valueDate.desc()).limit(limit).all()

    return [{
        "amount": t.amount,
        "type": t.type.value,
        "category": t.category,
        "narration": t.narration,
        "date": t.valueDate,
        "mode": t.mode
    }for t in transactions]

@router.get("category-breakdown")
def category_breakdown(
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label("total")
    ).filter(
        Transaction.user_id == current_user.id,
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

@router.get("/spending_trends/")
def spending_trends(
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = db.query(
        func.extract("month", Transaction.valueDate).label("month"),
        func.sum(Transaction.amount).label("expense")
    ).filter(
        Transaction.user_id == current_user.id,
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


@router.get("/insights")
def get_insights( month: int= datetime.now().month,
                year: int = datetime.now().year,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    data = gather_user_data(current_user.id, month, year, db)
    prompt = build_prompt(data, month, year)
    insights = get_ai_insights(prompt)


    return {
        "month": month,
        "year": year,
        "inights": insights
    }