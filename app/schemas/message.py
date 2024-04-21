from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageCreate(BaseModel):
    message: str
    created_by_user: Optional[str] = None
    created_by_bot: Optional[str] = None
    is_bot: bool = False

    class Config:
        from_attributes = True

class MessageGet(BaseModel):
    message_id: int
    chat_id: Optional[int]
    group_chat_id: Optional[int]
    user_id: Optional[str]
    bot_id: Optional[int]
    message: str
    created_by_user: Optional[str]
    created_by_bot: Optional[int]
    is_bot: bool
    created_at: datetime

    class Config:
        from_attributes = True