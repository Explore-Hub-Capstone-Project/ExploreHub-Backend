from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class User(BaseModel):
    email: str
    company: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class UserCreate(BaseModel):
    firstname: str = Field(..., min_length=1)
    lastname: str = Field(..., min_length=1)
    email: EmailStr
    mobile: str = Field(..., min_length=10)
    country: str
    password: str = Field(..., min_length=6)


class LoginSchema(BaseModel):
    email: str
    password: str


class AirportSearchData1(BaseModel):
    from_: str


class AirportSearchData2(BaseModel):
    to_: str
