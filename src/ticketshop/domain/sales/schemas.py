from datetime import datetime

from pydantic import BaseModel, Field


class SalesBase(BaseModel):
    id_user: int
    id_ticket: int
    count: int
    total_price: int
    sale_date: datetime


class SalesPublic(SalesBase):
    id_sale: int


class SalesUpdate(BaseModel):
    id_user: int | None = None
    id_ticket: int | None = None
    count: int | None = None
    total_price: int | None = None
    sale_date: datetime | None = None


class TicketPurchaseRequest(BaseModel):
    id_concert: int
    id_ticket_type: int
    count: int = Field(default=1, ge=1)