from datetime import datetime

from pydantic import BaseModel, Field

class ConcertBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    date: datetime
    id_hall: int
    description: str | None = None
    sales_paused: bool = False


class ConcertPublic(ConcertBase):
    id_concert: int


class ConcertUpdate(BaseModel):
    name: str | None = None
    date: datetime | None = None
    id_hall: int | None = None
    description: str | None = None
    sales_paused: bool | None = None


class PurchaseOptionItem(BaseModel):
    id_ticket_type: int
    ticket_type_name: str
    id_hall_zone: int
    price: int
    remains: int


class HallLayoutSeat(BaseModel):
    row: int
    seat: int


class HallLayoutZone(BaseModel):
    id_hall_zone: int
    id_ticket_type: int
    name: str
    role: str  # "vip" | "dance" | "lounge" | "other"
    price: int
    total: int
    remains: int
    color: str
    seats: list[HallLayoutSeat]


class HallLayoutResponse(BaseModel):
    scheme: str
    rows_count: int
    seats_per_row: int
    zones: list[HallLayoutZone]
    occupied: list[list[int]]  # [[row, seat], ...]