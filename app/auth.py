from pwdlib import PasswordHash
from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

ALGORITHM = "HS256"

password_hash = PasswordHash.recommended()

def hash_password(password: str):
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str):
    return password_hash.verify(password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode, SECRET_KEY, algorithm = ALGORITHM
    )