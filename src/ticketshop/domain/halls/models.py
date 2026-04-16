from typing import Optional
from sqlmodel import SQLModel, Field

class Hall(SQLModel, table=True):
    __tablename__ = "hall"
    id_hall: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    address: str | None = None
    phone: str
    seatsAmount: int | None = Field(default=None, ge=1)
    rows_count: int | None = Field(default=10, ge=1, le=100)
    seats_per_row: int | None = Field(default=10, ge=1, le=100)
    scheme: str | None = Field(default="classic", max_length=32)
