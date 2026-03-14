from pydantic import BaseModel, Field

class HallBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=200)
    phone: str = Field(min_length=1, max_length=20)
    seatsAmount: int = Field(ge=0, le=1000000)


class HallPublic(HallBase):
    id_hall: int


class HallUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    address: str | None = Field(default=None, min_length=1, max_length=200)
    phone: str | None = Field(default=None, min_length=1, max_length=20)
    seatsAmount: int | None = Field(default=None, ge=0, le=1000000)