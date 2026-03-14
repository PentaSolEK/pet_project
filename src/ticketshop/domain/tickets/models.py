from typing import Optional
from sqlmodel import SQLModel, Field

class Tickets(SQLModel, table=True):
    __tablename__ = "tickets"
    id_ticket: int = Field(default=None, primary_key=True)
    id_concert: int = Field(default=None, foreign_key="concert.id_concert")
    id_hall_zone: int = Field(default=None, foreign_key="hall_zone.id_hall_zone")
    price: int = Field(ge=0)
    remains: int = Field(ge=0)