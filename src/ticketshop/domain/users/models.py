from typing import Optional
from pydantic import EmailStr
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__ = "users"

    id_user: Optional[int] = Field(default=None, primary_key=True)
    name: str | None = None
    surname: str | None = None
    age: int | None = Field(default=None, gt=0, le=100)
    email: EmailStr = Field(index=True, unique=True)
    hashed_pass: str
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)