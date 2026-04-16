from pydantic import BaseModel, Field

class HallBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=200)
    phone: str = Field(min_length=1, max_length=20)
    seatsAmount: int = Field(ge=0, le=1000000)
    rows_count: int | None = Field(default=10, ge=1, le=100)
    seats_per_row: int | None = Field(default=10, ge=1, le=100)
    scheme: str | None = Field(default="classic", max_length=32)


class HallPublic(HallBase):
    id_hall: int


class HallUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    address: str | None = Field(default=None, min_length=1, max_length=200)
    phone: str | None = Field(default=None, min_length=1, max_length=20)
    seatsAmount: int | None = Field(default=None, ge=0, le=1000000)
    rows_count: int | None = Field(default=None, ge=1, le=100)
    seats_per_row: int | None = Field(default=None, ge=1, le=100)
    scheme: str | None = Field(default=None, max_length=32)
