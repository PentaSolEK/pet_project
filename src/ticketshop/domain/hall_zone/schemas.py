from pydantic import BaseModel, Field

class HallZoneBase(BaseModel):
    amount: int
    id_hall: int
    id_type: int

