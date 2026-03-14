from typing import Optional
from sqlmodel import SQLModel, Field

class HallZone(SQLModel, table=True):
    __tablename__ = "hall_zone"
    id_hall_zone: int = Field(default=None, primary_key=True)
    amount: int
    id_hall: int = Field(default=None, foreign_key='halls.id_hall')
    id_type: int = Field(default=None, foreign_key='tickettypes.id_type')