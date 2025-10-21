from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: EmailStr


class BuyTicketForm(BaseModel):
    concert_name: str
    ticket_count: int
    ticket_type: str
    user_mail: EmailStr
    user_name: str
    user_last_name: str
    user_age: int