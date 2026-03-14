from pydantic import BaseModel, Field

class TicketsBase(BaseModel):
    id_concert: int
    id_hall_zone: int
    price: int = Field(gt=0)
    remains: int = Field(ge=0)

