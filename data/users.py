from pydantic import EmailStr

from data.init_db import SessionDep
from sqlmodel import select

from models.db_models import Users, UsersBase, UsersRegistered


async def get_user_by_email(email: EmailStr, session: SessionDep):
    res = await session.exec(select(Users).where(Users.email == email))
    user = res.first()
    if user:
        return user
    return None


async def add_user_to_db(user_data: UsersRegistered, session: SessionDep):
    user = UsersBase(email=user_data.email, hashed_pass=user_data.password)
    db_user = Users.model_validate(user)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


