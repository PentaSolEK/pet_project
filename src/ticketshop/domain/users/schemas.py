from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id_user: int
    name: str | None = None
    surname: str | None = None
    age: int | None = Field(default=None, gt=0, le=100)
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=3, max_length=20)


class UserUpdate(BaseModel):
    name: str | None = None
    surname: str | None = None
    age: int | None = Field(default=None, gt=0, le=100)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=3, max_length=20)
    is_active: bool | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"