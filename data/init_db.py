<<<<<<< HEAD
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
=======
from sqlmodel import create_engine, Session
>>>>>>> b05e70515c495ef1fdffd9205744cc93d4447f51
from fastapi import Depends

from dotenv import load_dotenv
import os
from typing import Annotated

<<<<<<< HEAD
load_dotenv(r"/data/.env")
=======
load_dotenv(r"C:\Users\pazhi\PycharmProjects\projects\.venv\concert_app\data\CONCERT_DB.env")
>>>>>>> b05e70515c495ef1fdffd9205744cc93d4447f51

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

<<<<<<< HEAD
DB_URL = f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_async_engine(DB_URL, echo=True)


async def get_session():
    async with AsyncSession(engine) as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
=======

DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DB_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]




>>>>>>> b05e70515c495ef1fdffd9205744cc93d4447f51
