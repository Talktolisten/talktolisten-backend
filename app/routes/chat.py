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


@router.get("/{user_id}", response_model=List[chat.ChatGet])
def get_chats(
    user_id,
    db: Session = Depends(get_db),
    skip: int = 0,
):
    chats = (
        db.query(models.Chat)
        .join(models.Message, models.Message.chat_id == models.Chat.chat_id, isouter=True)
        .filter(models.Chat.user_id == user_id)
        .order_by(models.Message.created_at.desc())
        .offset(skip)
        .all()
    )
    return chats


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_chat(
    chat: chat.ChatCreate,
    db: Session = Depends(get_db),
):  
    new_chat = models.Chat(**chat.dict())
    num_bots = 5
    for i in range(2, num_bots+1):
        if new_chat.__getattribute__(f"bot_id{i}") == 0:
            new_chat.__setattr__(f"bot_id{i}", None)

    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)
    return new_chat


@router.delete("delete/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(
    chat_id: int,
    db: Session = Depends(get_db),
):  
    chat = db.query(models.Chat).filter(models.Chat.chat_id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    db.delete(chat)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)