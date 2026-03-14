from pydantic import EmailStr
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.ticketshop.domain.users.models import User


async def get_user_by_email(session: AsyncSession, email: EmailStr) -> User | None:
    res = await session.exec(select(User).where(User.email == email))
    return res.first()


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    return await session.get(User, user_id)


async def create_user(session: AsyncSession, *, email: EmailStr, hashed_pass: str) -> User:
    user = User(email=email, hashed_pass=hashed_pass)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(session: AsyncSession, user: User, **changes) -> User:
    for k, v in changes.items():
        if v is not None:
            setattr(user, k, v)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user