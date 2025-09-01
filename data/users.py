from data.init_db import SessionDep
from sqlmodel import select

from models.db_models import User

async def get_user_by_email(email: str, session: SessionDep):
    user = session.exec(select(User).where(User.email == email)).first()
    if user:
        return user
    return None