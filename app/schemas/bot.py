from pydantic import BaseModel
from typing import Optional

from pydantic.types import conint

class BotGet(BaseModel):
    bot_id: int
    bot_name: str
    short_description: Optional[str]
    description: str
    profile_picture: Optional[str]
    category: Optional[str]
    voice_id: int
    greeting: str
    num_chats: int
    likes: int
    created_by: str
    privacy: str
    gender: str

    class Config:
        from_attributes = True

class BotCreate(BaseModel):
    bot_name: str
    short_description: Optional[str]
    description: str
    greeting: str
    profile_picture: Optional[str]
    category: Optional[str]
    voice_id: int
    privacy: str
    gender: Optional[str]
    created_by: str

    class Config:
        from_attributes = True

class BotGenerate(BaseModel):
    bot_name: str
    description: str

    class Config:
        from_attributes = True

class BotUpdate(BaseModel):
    bot_name: Optional[str]
    short_description: Optional[str]
    description: Optional[str]
    profile_picture: Optional[str]
    voice_id: Optional[int]
    greeting: Optional[str]
    privacy: Optional[str]
    gender: Optional[str]

    class Config:
        from_attributes = True

class ImagePrompt(BaseModel):
    image_prompt: str

    class Config:
        from_attributes = True