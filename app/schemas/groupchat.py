from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .bot import BotGet

class GroupChatGet(BaseModel):
    group_chat_id: int
    group_chat_name: Optional[str] = None
    group_bots: Optional[list[BotGet]] = None
    group_chat_profile_picture: Optional[str] = None
    privacy: Optional[str] = None
    last_message_content: Optional[str] = None
    last_message_time: Optional[datetime] = None

    class Config:
        from_attributes = True

class GroupChatCreate(BaseModel):
    group_chat_name: str
    group_bots: Optional[list[int]] = None
    privacy: Optional[str] = None

    class Config:
        from_attributes = True

class GroupChatUpdate(BaseModel):
    group_chat_name: Optional[str]
    group_bots: Optional[list[int]]
    privacy: Optional[str]

    class Config:
        from_attributes = True


class VoiceGroupChat(BaseModel):
    group_chat_id: int
    text: str

    class Config:
        from_attributes = True