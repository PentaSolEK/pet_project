from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Concerts(SQLModel, table=True):
    __tablename__ = "concert"

    id_concert: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    date: datetime = Field(index=True)
    description: str | None = Field(default=None)
    sales_paused: bool = Field(default=False)

    id_hall: int | None = Field(default=None, foreign_key="hall.id_hall")


class ConcertGroup(SQLModel, table=True):
    __tablename__ = "concert_groups"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_concert: int = Field(foreign_key="concert.id_concert", index=True)
    id_group: int = Field(foreign_key="musicgroups.id_group", index=True)
