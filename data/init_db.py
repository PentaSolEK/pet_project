from sqlmodel import create_engine, Session
from fastapi import Depends

from dotenv import load_dotenv
import os
from typing import Annotated

load_dotenv(r"C:\Users\pazhi\PycharmProjects\projects\.venv\concert_app\data\CONCERT_DB.env")

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')


DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DB_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]




