from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter, Body
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import random
from sqlalchemy import func, select
from app import models
from app.config import configs, settings
from app.schemas import chat, bot, message, groupchat
from app.schemas.bot import BotGet
from app.api.api_v1.engines.storage.azure import azure_storage
from app.database import get_db
from app.auth import get_current_user
from app.api.api_v1.dependency.utils import *
from app.api.api_v1.engines.text.base import TextEngine, GroupChatTextEngine
from app.api.api_v1.engines.voice.base import VoiceEngine

router = APIRouter(
    prefix="/groupchat",
    tags=['GroupChat']
)


@router.get("/{user_id}",
            summary="Get all GroupChats of an user",
            description="Get all GroupChats of an user by user_id",
            response_model=List[groupchat.GroupChatGet])
def get_chats(
    user_id,
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    LatestMessageSubquery = (
        db.query(
            models.Message.group_chat_id,
            func.max(models.Message.created_at).label('latest_message_time'),
            func.max(models.Message.message_id).label('latest_message_id')  
        )
        .group_by(models.Message.group_chat_id)
        .subquery('latest_message_subquery')
    )

    MessageContentSubquery = (
        db.query(
            models.Message.message_id.label('latest_message_id'),
            models.Message.message.label('latest_message_content')
        )
        .subquery('message_content_subquery')
    )

    chats = (
        db.query(
            models.GroupChat,
            MessageContentSubquery.c.latest_message_content,
            LatestMessageSubquery.c.latest_message_time
        )
        .outerjoin(LatestMessageSubquery, models.GroupChat.group_chat_id == LatestMessageSubquery.c.group_chat_id)
        .outerjoin(MessageContentSubquery, LatestMessageSubquery.c.latest_message_id == MessageContentSubquery.c.latest_message_id)
        .filter(models.GroupChat.user_id == user_id)
        .order_by(LatestMessageSubquery.c.latest_message_time.desc())
        .offset(skip)
        .all()
    )

    chat_bots = {
        chat.group_chat_id: [
            BotGet.model_validate(bot)
            for bot in db.query(models.Bot)
                .join(models.GroupChatBots, models.Bot.bot_id == models.GroupChatBots.bot_id)
                .filter(models.GroupChatBots.group_chat_id == chat.group_chat_id)
                .all()
        ]
        for chat, _, _ in chats
    }

    results = []
    for chat, latest_message_content, latest_message_time in chats:
        chat_data = groupchat.GroupChatGet(
            group_chat_id=chat.group_chat_id,
            group_chat_name=chat.group_chat_name,
            group_bots=chat_bots[chat.group_chat_id],
            group_chat_profile_picture=chat.group_chat_profile_picture,
            privacy=chat.privacy,
            last_message_content=latest_message_content,
            last_message_time=latest_message_time
        )
        results.append(chat_data)

    return results


@router.get("/get_chat_by_id/{group_chat_id}",
            summary="Get a GroupChat",
            description="Get a GroupChat by group_chat_id",
            response_model=groupchat.GroupChatGet)
def get_chat_by_id(
    group_chat_id,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    chat = db.query(models.GroupChat).filter(models.GroupChat.group_chat_id == group_chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="GroupChat not found")

    chat_bots = [
        BotGet.model_validate(bot)
        for bot in db.query(models.Bot)
            .join(models.GroupChatBots, models.Bot.bot_id == models.GroupChatBots.bot_id)
            .filter(models.GroupChatBots.group_chat_id == group_chat_id)
            .all()
    ]

    response = groupchat.GroupChatGet(
        group_chat_id=chat.group_chat_id,
        group_chat_name=chat.group_chat_name,
        group_bots=chat_bots,
        group_chat_profile_picture=chat.group_chat_profile_picture,
        privacy=chat.privacy
    )
    return response


@router.post("/create",
                summary="Create a GroupChat",
                description="Create a GroupChat",
                response_model=groupchat.GroupChatGet)
def create_chat(
    chat_data: groupchat.GroupChatCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):  
    new_group_chat = models.GroupChat(
        user_id=current_user,
        group_chat_name=chat_data.group_chat_name,
        privacy=chat_data.privacy
    )
    db.add(new_group_chat)
    db.commit()
    db.refresh(new_group_chat)

    if chat_data.group_bots:
        for bot_id in chat_data.group_bots:
            db.add(models.GroupChatBots(group_chat_id=new_group_chat.group_chat_id, bot_id=bot_id))
        db.commit()

    # Add a bot message to the group chat
    all_bots = db.query(models.Bot).join(models.GroupChatBots).filter(models.GroupChatBots.group_chat_id == new_group_chat.group_chat_id).all()
    random_bot = random.choice(all_bots)
    text_engine = GroupChatTextEngine(message_list=[], all_bots=all_bots, random_bot_name=random_bot.bot_name)
    text_response = text_engine.get_response()
    new_bot_message = models.Message(
        group_chat_id=new_group_chat.group_chat_id,
        message=text_response,
        is_bot=True,
        created_by_bot=random_bot.bot_id
    )
    db.add(new_bot_message)
    db.commit()

    new_group_chat.last_message = new_bot_message.message_id
    db.commit()

    new_profile_picture = create_group_profile_picture([bot.profile_picture for bot in db.query(models.Bot).join(models.GroupChatBots).filter(models.GroupChatBots.group_chat_id == new_group_chat.group_chat_id).limit(4).all()])
    new_profile_picture.save(f"app/api/api_v1/dependency/temp_image/group_chat_{new_group_chat.group_chat_id}.webp")
    azure_storage.upload_blob(f"app/api/api_v1/dependency/temp_image/group_chat_{new_group_chat.group_chat_id}.webp", "group-chat-images", f"{new_group_chat.group_chat_id}.webp")
    os.remove(f"app/api/api_v1/dependency/temp_image/group_chat_{new_group_chat.group_chat_id}.webp")
    new_group_chat.group_chat_profile_picture = f"{settings.azure_db_endpoint}/group-chat-images/{new_group_chat.group_chat_id}.webp"
    db.commit()
    db.refresh(new_group_chat)

    response = groupchat.GroupChatGet(
        group_chat_id=new_group_chat.group_chat_id,
        group_chat_name=new_group_chat.group_chat_name,
        group_bots=all_bots,
        group_chat_profile_picture=new_group_chat.group_chat_profile_picture,
        privacy=new_group_chat.privacy,
        last_message_content=new_bot_message.message,
        last_message_time=new_bot_message.created_at
    )
    return response


@router.get("/{group_chat_id}/messages",
            summary="Get all Messages of a GroupChat",
            description="Get all Messages of a GroupChat by group_chat_id",
            response_model=List[message.MessageGet])
def get_messages(
    group_chat_id,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    messages = (
        db.query(models.Message)
        .join(models.User, models.Message.created_by_user == models.User.user_id, isouter=True)
        .join(models.Bot, models.Message.created_by_bot == models.Bot.bot_id, isouter=True)
        .filter(models.Message.group_chat_id == group_chat_id)
        .order_by(models.Message.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = [
        message.MessageGet(
            message_id=msg.message_id,
            chat_id=None,
            group_chat_id=msg.group_chat_id,
            user_id=msg.created_by_user,
            bot_id=msg.created_by_bot,
            message=msg.message,
            created_by_user=msg.created_by_user,
            created_by_bot=msg.created_by_bot,
            is_bot=msg.is_bot,
            created_at=msg.created_at
        )
        for msg in messages
    ]
    
    return result


@router.post("/{group_chat_id}/message",
            summary="Create a Message in a GroupChat",
            description="Create a Message in a GroupChat by group_chat_id",
            response_model=message.MessageGet,
            status_code=status.HTTP_201_CREATED)
def create_message(
    group_chat_id,
    message_obj: message.MessageCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    db_chat = db.query(models.GroupChat).filter(models.GroupChat.group_chat_id == group_chat_id).first()

    if not db_chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    new_message_data = message_obj.dict()
    new_message_data["group_chat_id"] = group_chat_id
    new_message = models.Message(**new_message_data)

    db.add(new_message)
    db.commit()

    last_chats = (
        db.query(models.Message)
        .filter(models.Message.group_chat_id == group_chat_id)
        .order_by(models.Message.created_at.desc())
        .limit(6)
        .all()
    )

    all_bots = db.query(models.Bot).join(models.GroupChatBots).filter(models.GroupChatBots.group_chat_id == group_chat_id).all()
    random_bot = random.choice(all_bots)

    message_list = []
    for last_chat in last_chats:
        if last_chat.is_bot:
            query_bot = db.query(models.Bot).filter(models.Bot.bot_id == last_chat.created_by_bot).first()
            new_message_obj = {
                "bot_name": query_bot.bot_name,
                "bot_description": query_bot.description,
                "message": last_chat.message
            }
        else:
            new_message_obj = {
                "bot_name": None,
                "bot_description": None,
                "message": last_chat.message
            }
        message_list.append(new_message_obj)
    
    text_engine = GroupChatTextEngine(message_list=message_list, all_bots=all_bots, random_bot_name=random_bot.bot_name)
    text_response = text_engine.get_response()

    new_bot_message = models.Message(
        group_chat_id=group_chat_id,
        message=text_response,
        is_bot=True,
        created_by_bot=random_bot.bot_id
    )

    db.add(new_bot_message)
    db.commit()

    db_chat.last_message = new_bot_message.message_id

    db.commit()
    db.refresh(db_chat)
    response = message.MessageGet(
        message_id=new_bot_message.message_id,
        chat_id=new_bot_message.chat_id,
        group_chat_id=new_bot_message.group_chat_id,
        user_id=current_user,
        bot_id=new_bot_message.created_by_bot,
        message=new_bot_message.message,
        created_by_user=new_bot_message.created_by_user,
        created_by_bot=new_bot_message.created_by_bot,
        is_bot=new_bot_message.is_bot,
        created_at=new_bot_message.created_at
    )
    return response


@router.patch("/{group_chat_id}",
            summary="Update a GroupChat",
            description="Update a GroupChat by group_chat_id",
            response_model=groupchat.GroupChatGet)
def update_chat(
    group_chat_id: int,
    chat_data: groupchat.GroupChatUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    db_group_chat = db.query(models.GroupChat).filter(models.GroupChat.group_chat_id == group_chat_id).first()

    if not db_group_chat:
        raise HTTPException(status_code=404, detail="GroupChat not found")
    
    if chat_data.group_chat_name:
        db_group_chat.group_chat_name = chat_data.group_chat_name

    if chat_data.group_bots:
        db.query(models.GroupChatBots).filter(models.GroupChatBots.group_chat_id == group_chat_id).delete()
        for bot_id in chat_data.group_bots:
            db.add(models.GroupChatBots(group_chat_id=group_chat_id, bot_id=bot_id))

    db.commit()
    db.refresh(db_group_chat)

    chat_bots = [
        BotGet.model_validate(bot)
        for bot in db.query(models.Bot)
            .join(models.GroupChatBots, models.Bot.bot_id == models.GroupChatBots.bot_id)
            .filter(models.GroupChatBots.group_chat_id == group_chat_id)
            .all()
    ]

    response = groupchat.GroupChatGet(
        group_chat_id=db_group_chat.group_chat_id,
        group_chat_name=db_group_chat.group_chat_name,
        group_bots=chat_bots,
        group_chat_profile_picture=db_group_chat.group_chat_profile_picture,
        privacy=db_group_chat.privacy
    )
    return response


@router.delete("/{group_chat_id}",
            summary="Delete a GroupChat",
            description="Delete a GroupChat by group_chat_id",
            status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(
    group_chat_id,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    chat = db.query(models.GroupChat).filter(models.GroupChat.group_chat_id == group_chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="GroupChat not found")
    db.delete(chat)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/process_audio/{group_chat_id}",
            summary="Process an voice audio message in a GroupChat",
            description="Process an voice audio message in a GroupChat by group_chat_id",
            status_code=status.HTTP_200_OK)
async def process_audio(
    group_chat_id: int,
    voice_chat: groupchat.VoiceGroupChat = Body(...),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    try:
        audio = voice_chat.text

        new_message = models.Message(
            group_chat_id=group_chat_id,
            message=audio,
            created_by_user=current_user,
            is_bot=False
        )

        db.add(new_message)
        db.commit()

        all_bots = db.query(models.Bot).join(models.GroupChatBots).filter(models.GroupChatBots.group_chat_id == group_chat_id).all()
        random_bot = random.choice(all_bots)

        last_chats = (
            db.query(models.Message)
            .filter(models.Message.group_chat_id == group_chat_id)
            .order_by(models.Message.created_at.desc())
            .limit(6)
            .all()
        )

        message_list = []
        for last_chat in last_chats:
            if last_chat.is_bot:
                query_bot = db.query(models.Bot).filter(models.Bot.bot_id == last_chat.created_by_bot).first()
                new_message_obj = {
                    "bot_name": query_bot.bot_name,
                    "bot_description": query_bot.description,
                    "message": last_chat.message
                }
            else:
                new_message_obj = {
                    "bot_name": None,
                    "bot_description": None,
                    "message": last_chat.message
                }
            message_list.append(new_message_obj)

        text_engine = GroupChatTextEngine(message_list=message_list, all_bots=all_bots, random_bot_name=random_bot.bot_name)
        text_response = text_engine.get_response()

        new_bot_message = models.Message(
            group_chat_id=group_chat_id,
            message=text_response,
            is_bot=True,
            created_by_bot=random_bot.bot_id
        )

        db.add(new_bot_message)
        db.commit()

        voice = (
            db.query(models.Voice)
            .join(models.Bot, models.Bot.voice_id == models.Voice.voice_id)
            .filter(models.Bot.bot_id == random_bot.bot_id)
            .first()
        )

        voice_service = VoiceEngine(text_response, voice, new_bot_message.message_id)
        output_audio = voice_service.get_audio_response()

        return {'audio': output_audio, 'message': text_response, 'bot_id': random_bot.bot_id}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))