from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.ticketshop.db.session import get_session
from src.ticketshop.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from src.ticketshop.domain.users.schemas import UserCreate, UserPublic, Token, UserUpdate
from src.ticketshop.domain.users.repo import get_user_by_email, create_user
from src.ticketshop.messaging.publishers.events import publish_user_registered
from src.ticketshop.domain.users.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, session: SessionDep):
    existing = await get_user_by_email(session, payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")

    hashed = get_password_hash(payload.password)
    user = await create_user(session, email=payload.email, hashed_pass=hashed)

    await publish_user_registered(payload.email)
    return user


@router.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
):
    user = await get_user_by_email(session, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=str(user.email))
    return Token(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserPublic)
async def me(current_user: CurrentUserDep):
    return current_user


@router.patch("/me", response_model=UserPublic)
async def patch_me(
    payload: UserUpdate,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    data = payload.model_dump(exclude_unset=True)
    if data.get("password"):
        current_user.hashed_pass = get_password_hash(data["password"])
    for field in ("name", "surname", "age"):
        if field in data:
            setattr(current_user, field, data[field])
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return current_user


@router.get("/get_user_by_mail", response_model=UserPublic)
async def get_by_mail(email: EmailStr, session: SessionDep):
    user = await get_user_by_email(session, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user