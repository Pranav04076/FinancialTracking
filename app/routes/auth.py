from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.db import get_db
from app.schemas import UserCreate, UserLogin
from app.models import User
from app.auth import hash_password, verify_password, create_access_token
from app.services.route_services.auth_service import register, login, logout,refresh_token
from app.schemas import RefreshTokenSchema
from app.dependencies import get_current_user
router = APIRouter(prefix = "/auth", tags = ["Authentication"])

@router.post("/register")
async def register_route(user: UserCreate, db: Session = Depends(get_db)):
    return register(user, db)


@router.post("/login/")
async def login_route(form_data: OAuth2PasswordRequestForm = Depends(), 
                db: Session = Depends(get_db)
                ):
    return login(form_data, db)



@router.post("/refresh")
def refresh_token_route(data: RefreshTokenSchema, db: Session = Depends(get_db)):

    return refresh_token(data, db)


@router.post("/logout")
def logout_route(current_user: User = Depends(get_current_user),
           db: Session = Depends(get_db)):
    return logout(current_user.id, db)