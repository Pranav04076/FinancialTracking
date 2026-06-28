from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.db import get_db
from app.schemas import UserCreate, UserLogin
from app.models import User
from app.auth import hash_password, verify_password, create_access_token, create_refresh_token
from uuid import UUID
from app.schemas import RefreshTokenSchema

def register(user: UserCreate, db: Session):
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

def login(form_data: OAuth2PasswordRequestForm, 
                db: Session = Depends(get_db)
                ):
    print("LOGIN HIT")
    db_user = (db.query(User).filter(User.email==form_data.username).first())

    if db_user is None:
        raise HTTPException(status_code=401,detail = "Invalid email or Password")
    
    if not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail = "Invalid email or password")
    
    token = create_access_token({"sub": str(db_user.id)})
    refresh_token = create_refresh_token()

    db_user.refresh_tokens = refresh_token
    db.commit() 

    
    return {
        "access_token": token, "token_type": "bearer",
        "refresh_token": refresh_token
    }


def refresh_token(data: RefreshTokenSchema, db: Session):
    user = db.query(User).filter(
        User.refresh_tokens == data.refresh_tokens

    ).first()

    if not user:
        raise HTTPException(status_code=401,detail="Invalid refresh token")

    # Generate new access token
    access_token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

def logout(user_id=UUID,
           db = Session
           ):
    
    current_user = db.query(User).filter(User.id==user_id).first()
    current_user.refresh_tokens = None
    db.commit()
    return {"message": "Logged out successfully"}