from pydantic import EmailStr

from data.init_db import SessionDep
from sqlmodel import select

from models.db_models import Users


async def get_user_by_email(email: EmailStr, session: SessionDep):
    res = await session.exec(select(Users).where(Users.email == email))
    user = res.first()
    if user:
        return user
    return None