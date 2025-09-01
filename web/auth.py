<<<<<<< HEAD
import asyncio
=======
>>>>>>> b05e70515c495ef1fdffd9205744cc93d4447f51
import os
from datetime import datetime, timedelta
from typing import Annotated
from dotenv import load_dotenv

import jwt
<<<<<<< HEAD
from fastapi import Depends, APIRouter, HTTPException, status
=======
from fastapi import Depends, FastAPI, HTTPException, status
>>>>>>> b05e70515c495ef1fdffd9205744cc93d4447f51
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

<<<<<<< HEAD
from data.init_db import SessionDep
from data import users
from models.db_models import UserPublic
=======
from data.users import get_user_by_email
from data.init_db import SessionDep
>>>>>>> b05e70515c495ef1fdffd9205744cc93d4447f51

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
<<<<<<< HEAD
router = APIRouter(prefix="/login", tags=["login"])
=======
app = FastAPI()
>>>>>>> b05e70515c495ef1fdffd9205744cc93d4447f51


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


<<<<<<< HEAD
async def authenticate_user(email: str, password: str, session: SessionDep):
    user = await users.get_user_by_email(email, session)
    if not user:
        return False
    if not verify_password(password, user.hashed_pass):
        return False
    return user





@router.get("/", response_model=UserPublic)
async def get_user(email, session: SessionDep):
    user = await users.get_user_by_email(email, session)
    return user

=======
async def get_user(email, session: SessionDep):
    user = await get_user_by_email(email, session)
    return user


res = get_user('epifan1980@example.org', SessionDep)
print(res)
>>>>>>> b05e70515c495ef1fdffd9205744cc93d4447f51
