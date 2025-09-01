from data.init_db import SessionDep
from sqlmodel import select

<<<<<<< HEAD
from models.db_models import Users

async def get_user_by_email(email: str, session: SessionDep):
    user = session.exec(select(Users).where(Users.email == email)).first()
=======
from models.db_models import User

async def get_user_by_email(email: str, session: SessionDep):
    user = session.exec(select(User).where(User.email == email)).first()
>>>>>>> b05e70515c495ef1fdffd9205744cc93d4447f51
    if user:
        return user
    return None