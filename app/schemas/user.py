from pydantic import BaseModel
from typing import Optional

from pydantic.types import conint


class UserCreate(BaseModel):
    user_id: str
    username: str
    gmail: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True
