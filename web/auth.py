from datetime import timedelta
from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from faststream.rabbit.fastapi import RabbitRouter

from data.init_db import SessionDep
from data import users
from models.db_models import UsersPublic, Users, Token, UsersBase, UsersRegistered
from service import auth as service


router = RabbitRouter(prefix="/auth", tags=["login"])


@router.post("/register", response_model=UsersPublic)
async def register(user_data: Annotated[UsersRegistered, Depends()], session: SessionDep):
    hashed_password = service.get_password_hash(user_data.password)
    user_data.password = hashed_password
    user_in_db = await users.add_user_to_db(user_data, session)
    await router.broker.publish(
        f"Зарегистрирован новый пользователь {user_data.email}",
        queue="registration"
    )
    return user_in_db


@router.post("/token", response_model=Token)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    user = await service.authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=service.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = service.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UsersPublic)
async def read_users_me(current_user: Annotated[Users, Depends(service.get_current_user)]):
    return current_user


@router.get("/get_user_by_mail", response_model=UsersPublic)
async def get_user_by_mail(email: EmailStr, session: SessionDep):
    user = await users.get_user_by_email(email, session)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    return user


