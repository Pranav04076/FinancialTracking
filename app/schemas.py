from enum import Enum

from pydantic import BaseModel, EmailStr

from datetime import date


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
    type: TransactionType
    mode: str
    amount: float
    valueDate: date
