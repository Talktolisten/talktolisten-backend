from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
from .. import models
from app.schemas import chat, message
from ..database import get_db


router = APIRouter(
    prefix="/chat",
    tags=['Chat']
)


@router.get("/{user_id}", 
            summary="Get all chats of an user",
            description="Get all chats of an user by user_id",
            response_model=List[chat.ChatGet])
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


@router.post("/", 
            summary="Create a new chat",
            description="Create a new chat",
            status_code=status.HTTP_201_CREATED)
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


@router.delete("/{chat_id}", 
            summary="Delete a chat",
            description="Delete a chat by chat_id",
            status_code=status.HTTP_204_NO_CONTENT)
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


@router.post("/{chat_id}/message", 
            summary="Create a new message for a chat",
            description="Create a new message",
            status_code=status.HTTP_201_CREATED)
def create_message(
    chat_id: int,
    message: message.MessageCreate,
    db: Session = Depends(get_db),
):  
    new_message = models.Message(**message.dict(), chat_id=chat_id)
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


@router.get("/{chat_id}/message", 
            summary="Get all messages of a chat",
            description="Get all messages of a chat by chat_id",
            response_model=List[message.MessageGet])
def get_messages(
    chat_id: int,
    db: Session = Depends(get_db),
    limit: int = 20,
    skip: int = 0,
):
    messages = (
        db.query(models.Message)
        .filter(models.Message.chat_id == chat_id)
        .order_by(models.Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return messages

@router.get("/{chat_id}/{message_id}", 
            summary="Get all messages of a chat",
            description="Get all messages of a chat by chat_id",
            response_model=List[message.MessageGet])
def get_messages(
    chat_id: int,
    message_id: int,
    db: Session = Depends(get_db),
    limit: int = 20,
    skip: int = 0,
):
    messages = (
        db.query(models.Message)
        .filter(models.Message.chat_id == chat_id)
        .filter(models.Message.message_id < message_id)
        .order_by(models.Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return messages

@router.delete("/{chat_id}/{message_id}", 
            summary="Delete a message",
            description="Delete a message by message_id",
            status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    chat_id: int,
    message_id: int,
    db: Session = Depends(get_db),
):  
    message = db.query(models.Message).filter(models.Message.message_id == message_id).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    db.delete(message)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)