from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
from app import models
from app.config import settings
from app.schemas import explore, groupchat
from app.schemas.bot import BotGet
from app.database import get_db
from app.auth import get_current_user


router = APIRouter(
    prefix="/explore",
    tags=['Explore']
)


@router.get("/", 
            summary="Get all bots",
            description="Get all bots in the database",
            response_model=List[explore.ExploreBots])
def get_bots(
    limit: int = 20, 
    skip: int = 0,
    current_user: dict= Depends(get_current_user),
    db: Session = Depends(get_db), 
):  
    bots = db.query(models.Bot).offset(skip).limit(limit).all()
    return bots


@router.get("/groupchat", 
            summary="Get all groupchat bots",
            description="Get all groupchat bots in the database",
            response_model=List[groupchat.GroupChatGet])
def get_groupchats(
    limit: int = 20, 
    skip: int = 0,
    db: Session = Depends(get_db), 
    current_user: dict= Depends(get_current_user),
):  
    db_groupchats = db.query(models.GroupChat).filter(
        models.GroupChat.privacy == 'public',
        models.GroupChat.user_id == settings.admin_id
        ).order_by(func.random()).offset(skip).limit(limit).all()
    
    response = []
    for chat in db_groupchats:
        chat_bots = [
            BotGet.model_validate(bot)
            for bot in db.query(models.Bot)
                .join(models.GroupChatBots, models.Bot.bot_id == models.GroupChatBots.bot_id)
                .filter(models.GroupChatBots.group_chat_id == chat.group_chat_id)
                .all()
        ]

        chat_response = groupchat.GroupChatGet(
            group_chat_id=chat.group_chat_id,
            group_chat_name=chat.group_chat_name,
            group_bots=chat_bots,
            group_chat_profile_picture=chat.group_chat_profile_picture,
            privacy=chat.privacy
        )
        response.append(chat_response)

    return response


@router.get("/search", 
            summary="Search bots by name",
            description="Search bots by name in the database",
            response_model=List[explore.ExploreBots])
def search_bots(
    search: str,
    limit: int = 20, 
    skip: int = 0, 
    current_user: dict= Depends(get_current_user),
    db: Session = Depends(get_db), 
):
    bots = db.query(models.Bot).filter(models.Bot.bot_name.contains(search),
                                    models.Bot.privacy == "public"
                                    ).offset(skip).limit(limit).all()
    return bots


@router.get("/category", 
            summary="Get bots by category",
            description="Get bots by category in the database",
            response_model=List[explore.ExploreBots])
def get_bots_by_category(
    category: str,
    limit: int = 20, 
    skip: int = 0, 
    db: Session = Depends(get_db), 
    current_user: dict= Depends(get_current_user),
):
    bots = db.query(models.Bot).filter(models.Bot.category == category,
                                    models.Bot.privacy == "public",
                                    ).order_by(func.random()).offset(skip).limit(limit).all()
    return bots


@router.get("/random", 
            summary="Get a bot randomly",
            description="Get a bot randomly in the database",
            response_model=explore.ExploreBots)
def get_bots_random(
    db: Session = Depends(get_db), 
    current_user: dict= Depends(get_current_user),
):
    bots = db.query(models.Bot).filter(models.Bot.privacy == "public").order_by(func.random()).limit(1).first()
    return bots


@router.get("/{id}", response_model=explore.ExploreBots)
def get_bot_by_id(
    id: int,
    db: Session = Depends(get_db), 
    current_user: dict= Depends(get_current_user),
):
    bot = db.query(models.Bot).filter(models.Bot.bot_id == id).first()

    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")

    return bot