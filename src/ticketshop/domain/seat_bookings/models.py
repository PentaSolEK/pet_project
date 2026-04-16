from typing import Optional
from sqlmodel import SQLModel, Field, UniqueConstraint


class SeatBooking(SQLModel, table=True):
    __tablename__ = "seat_booking"
    __table_args__ = (
        UniqueConstraint("id_concert", "row_num", "seat_num", name="uq_seat"),
    )

    id_seat_booking: Optional[int] = Field(default=None, primary_key=True)
    id_concert: int = Field(foreign_key="concert.id_concert", index=True)
    id_hall_zone: int = Field(foreign_key="hall_zone.id_hall_zone", index=True)
    row_num: int = Field(ge=0)
    seat_num: int = Field(ge=1)
    id_sale: Optional[int] = Field(default=None, foreign_key="sales.id_sale")
