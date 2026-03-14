from datetime import datetime

from pydantic import BaseModel, Field

class ConcertBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    date: datetime
    id_hall: int

class ConcertPublic(ConcertBase):
    id_concert: int

class ConcertUpdate(BaseModel):
    name: str | None = None
    date: datetime | None = None
    id_hall: int | None = None