from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from app.models import Budget, Transaction
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.db import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import BudgetCreate, BudgetUpdate, TransactionType

router = APIRouter(prefix = "/budget", tags = ["budgets"])

@router.post("/add_budget")
def add_budget(data: BudgetCreate,
               db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    
    new_budget = Budget(
        user_id = current_user.id,
        category = data.category.strip().title(),
        monthly_limit = data.monthly_limit
    )

    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)

    return new_budget


@router.get("/get_budget")
def get_budget(db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    budget_set = db.query(Budget).filter(Budget.user_id==current_user.id).all()

    return budget_set

@router.put("/update_budget/{category}")
def update_budget(category: str,
                  new_limit: BudgetUpdate, 
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    category = category.lower()
    budget_data = db.query(Budget).filter(
                                            Budget.category.lower() == category,
                                            Budget.user_id==current_user.id
                                                ).first()

    
    if budget_data is None: 
        raise HTTPException(status_code=401, detail = 'Category not found')
    
    budget_data.monthly_limit = new_limit

    db.commit()
    db.refresh(budget_data)

    return{
        "id": budget_data.id,
        "user_id": budget_data.user_id,
        "category": budget_data.category,
        "new_limit": budget_data.monthly_limit
    }


@router.delete("/delete_budget/{category}")
def delete_budget(category: str, 
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    
    budget_data = db.query(Budget).filter(Budget.category == category,
                                          Budget.user_id==current_user.id).first()
    
    db.delete(budget_data)
    db.commit()

    return {
        "message": f"{category} Budget Deleted Successfully"
    }


@router.get("/status")
def get_budget_status(month: int = datetime.now().month,
                      year: int = datetime.now().year,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):


    budgets = db.query(Budget).filter(Budget.user_id==current_user.id).all()

    if not budgets:
        raise HTTPException(status_code=401, detail = "No budgets set")
    
    result = []
        
    for budget in budgets:
        spent = db.query(func.sum(Transaction.amount)).filter(Transaction.user_id==current_user.id,
                                             Transaction.category==budget.category,
                                             Transaction.type == TransactionType.DEBIT,
                                             extract("month", Transaction.valueDate)==month,
                                             extract("year", Transaction.valueDate)==year).scalar() or 0
        
        remaining = budget.monthly_limit-spent
        utilization = round((spent/budget.monthly_limit)*100,2)
        alert = utilization>=80

        result.append({
            "category": budget.category,
            "monthly_limit": budget.monthly_limit,
            "spend": spent,
            "remaining": remaining,
            "utilization": utilization,
            "alert": alert,
            "status": "EXCEEDED" if spent > budget.monthly_limit else "WARNING" if alert else "OK"
        })

    return result






