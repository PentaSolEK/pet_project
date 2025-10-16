import os
from typing import Annotated

from dotenv import load_dotenv
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import EmailStr
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, status, Depends
from datetime import datetime, timedelta

from data import users
from data.init_db import SessionDep
from models.other_models import TokenData

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")



def get_password_hash(password):
    return password_hash.hash(password)


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


async def authenticate_user(email: EmailStr, password: str, session: SessionDep):
    user = await users.get_user_by_email(email, session)
    if not user:
        return False
    if not verify_password(password, user.hashed_pass):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: EmailStr = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = await users.get_user_by_email(token_data.email, session)
    if user is None:
        raise credentials_exception
    return user