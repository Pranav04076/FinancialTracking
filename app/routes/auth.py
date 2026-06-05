from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.db import get_db
from app.schemas import UserCreate, UserLogin
from app.models import User
from app.auth import hash_password, verify_password, create_access_token


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
async def login(form_data: OAuth2PasswordRequestForm = Depends(), 
                db: Session = Depends(get_db)
                ):
    print("LOGIN HIT")
    db_user = (db.query(User).filter(User.email==form_data.username).first())

    if db_user is None:
        raise HTTPException(status_code=401,detail = "Invalid email or Password")
    
    if not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail = "Invalid email or password")
    
    token = create_access_token({"sub": str(db_user.id)})

    
    return {
        "access_token": token, "token_type": "bearer"
    }