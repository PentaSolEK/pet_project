from pydantic import BaseModel, Field

class TickettypesBase(BaseModel):
    type: str = Field(min_length=1, max_length=100)


class TickettypesPublic(TickettypesBase):
    id_type: int


class TickettypesUpdate(BaseModel):
    type: str | None = Field(default=None, min_length=1, max_length=100)