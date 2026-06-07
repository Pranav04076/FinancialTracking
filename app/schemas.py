from enum import Enum

from pydantic import BaseModel, EmailStr, field_validator

from datetime import date

from typing import Optional

from uuid import UUID

class TransactionType(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TransactionCreate(BaseModel):
    txn_id: Optional[str] = None
    type: TransactionType
    mode: str
    amount: float
    valueDate: date
    narration: str

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v<= 0:
            raise ValueError("Amount must be greater than 0")
        return v
    
    @field_validator("valueDate")
    @classmethod
    def not_future_date(cls, v):
        if v> date.today():
            raise ValueError("Transaction date cannot be in future")
        
        return v

class TransactionResponse(BaseModel):
    id: UUID
    txn_id: Optional[str] = None
    type: TransactionType
    mode: str
    amount: float
    valueDate: date
    narration: str
    category: str

    class Config:
        from_attributes = True

class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    mode: Optional[str] = None
    narration: Optional[str] = None
    valueDate: Optional[date] = None
    category: Optional[str]

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v<= 0:
            raise ValueError("Amount must be greater than 0")
        return v
    
    @field_validator("valueDate")
    @classmethod
    def not_future_date(cls, v):
        if v>= date.today():
            raise ValueError("Transaction date cannot be in future")
        
        return v
    

class BudgetCreate(BaseModel):
    category: str
    monthly_limit: float

class BudgetUpdate(BaseModel):
    monthly_limit: float

class BudgetResponse(BaseModel):
    id: UUID
    user_id: UUID
    category: str
    monthly_limit: float
    class Config:
        from_attributes = True