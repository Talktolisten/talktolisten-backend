from pydantic import BaseModel
from typing import Optional


class ChatModel(BaseModel):
    user_id: str
    bot_id1: int
    bot_id2: Optional[int] = None
    bot_id3: Optional[int] = None
    bot_id4: Optional[int] = None
    bot_id5: Optional[int] = None
    last_message: Optional[int] = None

    class Config:
        orm_mode = True


# user sent id
class user_id(BaseModel):
    user_id: str


class create_chat_info(BaseModel):
    chat_id: int
    user_id: str
    bot_id1: int

    class Config:
        orm_mode = True
