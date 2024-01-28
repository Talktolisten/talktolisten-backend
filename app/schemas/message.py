from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageCreate(BaseModel):
    user_id: str
    bot_id: int
    message: str
    created_by_user: Optional[str] = None
    created_by_bot: Optional[str] = None
    is_bot: bool = False

    class Config:
        from_attributes = True

class MessageGet(BaseModel):
    message_id: int
    chat_id: int
    user_id: str
    bot_id: str
    message: str
    created_by_user: Optional[str]
    created_by_bot: Optional[str]
    is_bot: bool
    created_at: datetime

    class Config:
        from_attributes = True