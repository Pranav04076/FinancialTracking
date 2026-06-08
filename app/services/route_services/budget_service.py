from uuid import UUID
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.schemas import BudgetCreate, BudgetUpdate, TransactionType
from app.models import Budget, Transaction

def add_budget(user_id: UUID,
            data: BudgetCreate,
            db: Session,
               ):
    
    new_budget = Budget(
        user_id = user_id,
        category = data.category.strip().title(),
        monthly_limit = data.monthly_limit
    )

    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)

    return new_budget

def get_budget(db: Session,
               user_id: UUID
):
    budget_set = db.query(Budget).filter(Budget.user_id==user_id).all()

    return budget_set

def update_budget(category: str,
                  user_id: UUID,
                  new_limit: BudgetUpdate, 
                  db: Session):
    category = category.lower()
    budget_data = db.query(Budget).filter(
                                            Budget.category.lower() == category,
                                            Budget.user_id==user_id
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


def delete_budget(category: str, 
                  db: Session,
                  user_id: UUID):
    
    budget_data = db.query(Budget).filter(Budget.category == category,
                                          Budget.user_id==user_id).first()
    
    db.delete(budget_data)
    db.commit()

    return {
        "message": f"{category} Budget Deleted Successfully"
    }


def get_budget_status(user_id: UUID,
                    db: Session,
                    month: int = datetime.now().month,
                    year: int = datetime.now().year,
                    ):


    budgets = db.query(Budget).filter(Budget.user_id==user_id).all()

    if not budgets:
        raise HTTPException(status_code=401, detail = "No budgets set")
    
    result = []
        
    for budget in budgets:
        spent = db.query(func.sum(Transaction.amount)).filter(Transaction.user_id==user_id.id,
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