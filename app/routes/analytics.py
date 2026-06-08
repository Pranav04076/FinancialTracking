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
from app.services.route_services.analytics_service import (get_balance, total_debit, total_credit, monthly_income, monthly_expense, monthly_net, 
                                                           largest_expense, largest_income, avg_transaction, transactions_between,
                                                           get_monthly_savings, get_recent_transactions, category_breakdown,
                                                           spending_trends, get_insights)


router = APIRouter(prefix = "/analytics", tags = ["analytics"])

@router.get("/balance/")
def get_balance_route(db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    return get_balance(db, current_user.id)


@router.get("/total_debit/")
def total_debit_route(db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    return total_debit(db, current_user.id)

@router.get("/total_credit/")
def total_credit_route(db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    return total_credit(db, current_user.id)


@router.get("/monthly_income/")
def monthly_income_route(month: int,
                   year: int,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    
    return monthly_income(month, year, db, current_user.id)
                  


@router.get("/monthly_expense/")
def monthly_expense_route(month: int,
                   year: int,
                   db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    
   return monthly_expense(month, year, db, current_user.id)


@router.get("/monthly_net/")
def monthly_net_route(month: int, 
                year: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    return monthly_net(month, year, db, current_user.id)
    

@router.get("/largest_expense")
def largest_expense_route(month: int, 
                year: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    return largest_expense(month, year, db, current_user.id)

@router.get("/largest_income")
def largest_income_route(month: int, 
                year: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    return largest_income(month, year, db, current_user.id)


@router.get("/avg_transaction_amount/")
def avg_transaction_route(month: int, 
                year: int,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    return avg_transaction(month, int, db, current_user.id)

@router.get("/transactions-between/")
def transactions_between_route(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: User= Depends(get_current_user)
):
    return transactions_between(start_date, end_date, db, current_user.id)

@router.get("/monthly_savings")
def get_monthly_savings_route(month: int = datetime.now().month,
                        year: int = datetime.now().year,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    
   return get_monthly_savings(db, current_user.id, month, year)

@router.get("/recent_transactions")
def get_recent_transactions_route(limit: int = 10,
                            db: Session = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    
    return get_recent_transactions(db, current_user.id, limit)


@router.get("category-breakdown")
def category_breakdown_route(
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return category_breakdown(month, year, db, current_user.id)

@router.get("/spending_trends/")
def spending_trends_route(
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return spending_trends(year, db, current_user.id)


@router.get("/insights")
def get_insights_route( month: int= datetime.now().month,
                year: int = datetime.now().year,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    
    return get_insights(db, current_user.id, month, year)