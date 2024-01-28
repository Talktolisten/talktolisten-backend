from pydantic import BaseModel
from typing import Optional

from pydantic.types import conint


class ExploreBots(BaseModel):
    bot_id: int
    bot_name: str
    short_description: Optional[str]
    description: str
    profile_picture: Optional[str]
    category: Optional[str]
    voice_id: int
    num_chats: int
    likes: int
    created_by: str

    class Config:
        from_attributes = True