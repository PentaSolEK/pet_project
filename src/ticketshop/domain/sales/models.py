from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Sale(SQLModel, table=True):
    __tablename__ = "sales"

    id_sale: Optional[int] = Field(default=None, primary_key=True)
    id_user: int = Field(foreign_key="users.id_user", index=True)
    id_ticket: int = Field(foreign_key="tickets.id_ticket", index=True)

    count: int = Field(default=1, ge=1)
    total_price: int = Field(ge=0)

    sale_date: datetime = Field(default=datetime.now())
