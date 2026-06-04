from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import UserCreate, UserLogin
from app.models import User
from app.auth import hash_password, verify_password


router = APIRouter(prefix = "/auth", tags = ["Authentication"])

@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    email_exists = db.query(User).filter(User.email==user.email).first()

    if email_exists:
        raise HTTPException(status_code= 409, detail= "Email already exists")
    new_user = User(
        username=user.username, 
        email = user.email,
        hashed_password = hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
    "id": new_user.id,
    "username": new_user.username
    }


@router.post("/login/")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = (db.query(User).filter(User.email==user.email).first())

    if db_user is None:
        raise HTTPException(status_code=401,detail = "Invalid email or Password")
    
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail = "Invalid email or password")
    
    return {
        "message": "Login Successful",
        "id": db_user.id
    }