from pydantic import BaseModel, Field
from typing import Optional

from pydantic.types import conint


class UserCreate(BaseModel):
    user_id: str
    username: str
    gmail: str
    first_name: str
    last_name: str
    dob: Optional[str]

    class Config:
        from_attributes = True

class UserGet(BaseModel):
    user_id: str
    username: str
    gmail: str
    first_name: str
    last_name: str
    dob: Optional[str]
    subscription: str
    bio: Optional[str]
    profile_picture: Optional[str]
    status: str
    theme: str

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, example="new_username")
    gmail: Optional[str] = Field(None, example="new_email@gmail.com")
    first_name: Optional[str] = Field(None, example="John")
    last_name: Optional[str] = Field(None, example="Doe")
    dob: Optional[str] = Field(None, example="01 / 01 / 1999")
    subscription: Optional[str] = Field(None, example="premium")
    bio: Optional[str] = Field(None, example="Updated bio")
    profile_picture: Optional[str] = Field(None, example="url/to/new/picture.jpg")
    status: Optional[str] = Field(None, example="active")
    theme: Optional[str] = Field(None, example="dark")

    class Config:
        from_attributes = True