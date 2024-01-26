from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
from .. import models
from app.schemas import chat
from ..database import get_db


router = APIRouter(
    prefix="/chat",
    tags=['Chat']
)


# get all chats by userid
@router.get("/{user_id}", response_model=List[chat.ChatModel])
def get_chats(
    user_id,
    db: Session = Depends(get_db),
    limit: int = 20,
    skip: int = 0,
):
    query = db.query(models.Chat)

    query = query.filter(models.Chat.user_id == user_id)

    chats = query.offset(skip).limit(limit).all()
    return chats


# create a new chat
@router.post("/")
def create_chat(
    chat: chat.create_chat_info,
    db: Session = Depends(get_db),
):
    new_chat = models.Chat(
        chat_id=chat.chat_id,
        user_id=chat.user_id,
        bot_id1=chat.bot_id1,
    )

    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat
