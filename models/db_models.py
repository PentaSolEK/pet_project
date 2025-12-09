from sqlmodel import SQLModel, Field
from datetime import datetime
from pydantic import EmailStr, BaseModel

class MusicgroupsBase(SQLModel):
    name: str
    albumCount: int = Field(index=True)
    site: str
    id_genre: int = Field(index=True)


class Musicgroups(MusicgroupsBase, table=True):
    id_group: int = Field(default=None, primary_key=True)


class MusicgroupsPublic(MusicgroupsBase):
    id_group: int


class MusicgroupsUpdate(SQLModel):
    name: str | None = None
    albumCount: int | None = None
    site: str | None = None
    id_genre: int | None = None


class Concert_groupsBase(SQLModel):
    id_group: int
    id_concert: int


class Concert_groups(Concert_groupsBase):
    id_concert_groups: int = Field(default=None, primary_key=True)


class TickettypesBase(SQLModel):
    type: str
    price: int


class Tickettypes(TickettypesBase, table=True):
    id_type: int = Field(default=None, primary_key=True)


class TickettypesPublic(TickettypesBase):
    id_type: int


class TickettypesUpdate(SQLModel):
    type: str | None = None
    price: int | None = None


class TicketsBase(SQLModel):
    id_concert: int
    id_hall_ticketTypes: int


class Tickets(TicketsBase, table=True):
    id_ticket: int = Field(default=None, primary_key=True)


class HallBase(SQLModel):
    address: str
    phone: str
    seatsAmount: int = Field(index=True)


class Hall(HallBase, table=True):
    number: int | None = Field(default=None, primary_key=True)


class HallPublic(HallBase):
    number: int


class HallUpdate(SQLModel):
    address: str | None = None
    phone: str | None = None
    seatsAmount: str | None = None


class ConcertBase(SQLModel):
    name: str = Field(description="Название концерта")
    date: datetime = Field(index=True)
    id_hall: int


class Concert(ConcertBase, table=True):
    id_concert: int = Field(default=None, primary_key=True)


class ConcertPubic(ConcertBase):
    id_concert: int


class ConcertUpdate(SQLModel):
    name: str | None = None
    date: str | None = None
    id_hall: int | None = None


class Hall_TicketTypesBase(SQLModel):
    amount: int
    id_hall: int
    id_type: int


class Hall_TicketTypes(Hall_TicketTypesBase, table=True):
    id_hall_ticketTypes: int = Field(default=None, primary_key=True)


class SalesBase(SQLModel):
    id_user: int = Field(index=True)
    id_ticket: int = Field(index=True)
    count: int
    sale_date: datetime = Field(index=True)


class Sales(SalesBase, table=True):
    id_sale: int = Field(default=None, primary_key=True)


class SalesPublic(SalesBase):
    id_sale: int


class SalesUpdate(SQLModel):
    id_user: int | None = None
    id_ticket: int | None = None
    count: int | None = None
    sale_date: datetime | None = None


class UsersBase(SQLModel):
    name: str | None = None
    surname: str | None = None
    age: int | None = Field(gt=0, le=100, default=None)
    email: EmailStr
    hashed_pass: str = Field(min_length=3, max_length=100)
    is_active: bool = Field(default=True)


class Users(UsersBase, table=True):
    id_user: int = Field(default=None, primary_key=True)


class UsersPublic(SQLModel):
    name: str | None
    surname: str | None
    age: int | None = Field(gt=0, le=100)
    email: EmailStr
    is_active: bool = Field(default=True)
    id_user: int


class UsersUpdate(SQLModel):
    name: str | None = None
    surname: str | None = None
    age: int | None = None
    email: EmailStr | None = None
    hashed_pass: str | None = None
    is_active: bool | None = None


class UsersRegistered(SQLModel):
    email: EmailStr
    password: str = Field(min_length=3, max_length=20)




