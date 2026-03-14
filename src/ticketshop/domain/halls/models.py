from typing import Optional
from sqlmodel import SQLModel, Field

class Hall(SQLModel, table=True):
    __tablename__ = "hall"
    id_hall: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    address: str | None = None
    phone: str
    seatsAmount: int | None = Field(default=None, ge=1)