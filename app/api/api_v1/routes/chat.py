from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func, select
from app import models
from app.schemas import chat, message
from app.database import get_db
from app.auth import get_current_user


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
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    stmt = (
        select(models.Chat.chat_id, models.Chat.user_id, models.Bot.bot_id,
               models.Bot.bot_name, models.Bot.profile_picture)
        .select_from(models.Chat)
        .join(models.Bot, models.Bot.bot_id == models.Chat.bot_id1)
        .join(models.Message, models.Message.chat_id == models.Chat.chat_id, isouter=True)
        .filter(models.Chat.user_id == user_id)
        .order_by(models.Message.created_at.desc())
    )

    result = db.execute(stmt).fetchall()
    # Convert tuples into dictionaries
    chats = [
        {
            "chat_id": row[0],
            "user_id": row[1],
            "bot_id1": row[2],
            "bot_id1_name": row[3],
            "bot_id1_profile_picture": row[4],
        }
        for row in result
    ]
    return chats


@router.post("/",
             summary="Create a new chat",
             description="Create a new chat",
             status_code=status.HTTP_201_CREATED)
def create_chat(
    chat: chat.ChatCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
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
    current_user: str = Depends(get_current_user),
):  
    chat = db.query(models.Chat).filter(models.Chat.chat_id == chat_id).first()
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
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
    current_user: str = Depends(get_current_user),
):  
    
    db_chat = db.query(models.Chat).filter(models.Chat.chat_id == chat_id).first()

    if not db_chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    new_message_data = message.dict()
    new_message_data["chat_id"] = chat_id
    new_message = models.Message(**new_message_data)

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
    limit: int = 20,
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    messages = (
        db.query(
            models.Message.message_id,
            models.Message.chat_id,
            models.Message.message,
            models.Message.created_at,
            models.Message.created_by_user,
            models.Message.created_by_bot,
            models.Message.is_bot,
            models.Chat.user_id,
            models.Chat.bot_id1.label('bot_id')
        )
        .join(models.Chat, models.Message.chat_id == models.Chat.chat_id)
        .filter(models.Message.chat_id == chat_id)
        .order_by(models.Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .yield_per(30)
        .all()
    )

    return [
        message.MessageGet(
            message_id=msg.message_id,
            chat_id=msg.chat_id,
            message=msg.message,
            created_at=msg.created_at,
            created_by_user=msg.created_by_user,
            created_by_bot=msg.created_by_bot,
            is_bot=msg.is_bot,
            user_id=msg.user_id,
            bot_id=msg.bot_id
        ) for msg in messages
    ]


@router.get("/{chat_id}/{message_id}",
            summary="Get a specific message in a chat",
            description="Get a specific message in a chat",
            response_model=message.MessageGet)
def get_message(
    chat_id: int,
    message_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    message = (
        db.query(models.Message)
        .filter(models.Message.chat_id == chat_id)
        .filter(models.Message.message_id == message_id)
        .first()
    )

    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")

    return message


@router.get("/{chat_id}/{message_id}",
            summary="Get older messages in a chat",
            description="Get messages older than a specific message in a chat",
            response_model=List[message.MessageGet])
def get_older_messages(
    chat_id: int,
    message_id: int,
    limit: int = 20,
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    messages = (
        db.query(
            models.Message.message_id,
            models.Message.chat_id,
            models.Message.message,
            models.Message.created_at,
            models.Message.created_by_user,
            models.Message.created_by_bot,
            models.Message.is_bot,
            models.Chat.user_id,
            models.Chat.bot_id1.label('bot_id')
        )
        .join(models.Chat, models.Message.chat_id == models.Chat.chat_id)
        .filter(models.Message.chat_id == chat_id, models.Message.message_id < message_id)
        .order_by(models.Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        message.MessageGet(
            message_id=msg.message_id,
            chat_id=msg.chat_id,
            message=msg.message,
            created_at=msg.created_at,
            created_by_user=msg.created_by_user,
            created_by_bot=msg.created_by_bot,
            is_bot=msg.is_bot,
            user_id=msg.user_id,
            bot_id=msg.bot_id
        ) for msg in messages
    ]


@router.delete("/{chat_id}/{message_id}",
               summary="Delete a message",
               description="Delete a message by message_id",
               status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    chat_id: int,
    message_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):  
    message = db.query(models.Message).filter(models.Message.message_id == message_id).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    db.delete(message)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
