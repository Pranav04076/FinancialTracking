from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.auth import SECRET_KEY, ALGORITHM
from app.db import get_db
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login/")

def get_current_user(token: str = Depends(oauth2_scheme),
                     db = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code = 401, detail = 'Invalid Token')
        
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = (db.query(User).filter(User.id==user_id)).first()

    if user is None: 
        raise HTTPException(
            status_code=401,
            detail="User not Found"
        )
    
    return user
