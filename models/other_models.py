from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: EmailStr


class BuyTicketForm(BaseModel):
    concert_name: str = Field(description="Название концерта")
    ticket_count: int = Field(description="Количество билетов")
    ticket_type: str = Field(description="Тип билета: DANCE FLOOR, LOUNGE, VIP")
    user_mail: EmailStr = Field(description="Почта покупателя")
    user_name: str = Field(description="Имя покупателя")
    user_last_name: str = Field(description="Фамилия покупателя")
    user_age: int = Field(description="Возраст покупателя")