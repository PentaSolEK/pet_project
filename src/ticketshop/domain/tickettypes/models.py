from typing import Optional
from sqlmodel import SQLModel, Field

class TicketType(SQLModel, table=True):
    __tablename__ = "tickettypes"
    id_type: int = Field(default=None, primary_key=True)
    type: str