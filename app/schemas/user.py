from pydantic import BaseModel
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