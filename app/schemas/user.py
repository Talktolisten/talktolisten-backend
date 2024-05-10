from pydantic import BaseModel
from typing import Optional, List

from pydantic.types import conint


class UserCreate(BaseModel):
    user_id: str
    username: str
    gmail: str
    first_name: str
    last_name: str
    profile_picture: str
    bio: Optional[str]
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
    username: Optional[str] = None
    gmail: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    dob: Optional[str] = None
    subscription: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    status: Optional[str] = None
    theme: Optional[str] = None

    class Config:
        from_attributes = True

class FeedbackReport(BaseModel):
    feedback: Optional[str]
    report: Optional[str]
    pictures: Optional[List[str]]

    class Config:
        from_attributes = True