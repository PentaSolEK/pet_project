
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends

from dotenv import load_dotenv
import os
from typing import Annotated


load_dotenv()

class Init_DB:
    def __init__(self):
        self.engine = None
        self.DB_USER = os.getenv('DB_USER')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD')
        self.DB_HOST = os.getenv('DB_HOST')
        self.DB_NAME = os.getenv('DB_NAME')

    def init_engine(self):
        """Инициализация движка и сессии"""
        DB_URL = f"mysql+asyncmy://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.DB_NAME}"

        self.engine = create_async_engine(
            DB_URL,
            echo=True,  # Логирование SQL запросов
        )

    async def get_session(self):
        """Зависимость для получения сессии"""
        async with AsyncSession(self.engine) as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

db_manager = Init_DB()

# Инициализируем движок при импорте
db_manager.init_engine()

SessionDep = Annotated[AsyncSession, Depends(db_manager.get_session)]
