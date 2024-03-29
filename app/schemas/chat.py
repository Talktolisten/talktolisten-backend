from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatGet(BaseModel):
    chat_id: int
    user_id: str
    bot_id1: int
    bot_id1_name: str
    bot_id1_profile_picture: str
    bot_id2: Optional[int] = None
    bot_id3: Optional[int] = None
    bot_id4: Optional[int] = None
    bot_id5: Optional[int] = None
    last_message_content: Optional[str] = None
    last_message_time: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatCreate(BaseModel):
    user_id: str
    bot_id1: int
    bot_id2: Optional[int] = None
    bot_id3: Optional[int] = None
    bot_id4: Optional[int] = None
    bot_id5: Optional[int] = None

    class Config:
        from_attributes = True


class VoiceChat(BaseModel):
    chat_id: int
    bot_id: int
    text: str

    class Config:
        from_attributes = True