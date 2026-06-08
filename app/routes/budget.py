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
from app.services.route_services.budget_service import add_budget, get_budget, update_budget, delete_budget, get_budget_status

router = APIRouter(prefix = "/budget", tags = ["budgets"])

@router.post("/add_budget")
def add_budget_route(data: BudgetCreate,
               db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    
    return add_budget(current_user.id, data, db)


@router.get("/get_budget")
def get_budget_route(db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    return get_budget(db, current_user.id)

@router.put("/update_budget/{category}")
def update_budget_route(category: str,
                  new_limit: BudgetUpdate, 
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    return update_budget(category, current_user.id, new_limit, db)


@router.delete("/delete_budget/{category}")
def delete_budget_route(category: str, 
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    
    return delete_budget(category, db, current_user.id)


@router.get("/status")
def get_budget_status_route(month: int = datetime.now().month,
                      year: int = datetime.now().year,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    
    return get_budget_status(current_user, db, month, year)

    






