from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
from app import models
from app.schemas import bot
from app.database import get_db
from app.auth import get_current_user


router = APIRouter(
    prefix="/bot",
    tags=['bot']
)

@router.get("/{userID}", 
            summary="Get all bots created by user",
            description="Get all bots created by an user",
            response_model=List[bot.BotGet])
def get_bots(
    userID: str,
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    return db.query(models.Bot).filter(models.Bot.created_by == userID).all()


@router.post("/", 
            summary="Create a new bot",
            description="Create a new bot",
            response_model=bot.BotGet, status_code=status.HTTP_201_CREATED)
def create_bot(
    bot_create: bot.BotCreate,
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    db_bot = models.Bot(**bot_create.dict())
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot


@router.patch("/{id}", 
            summary="Update bot information",
            description="Update bot information by bot id",
            response_model=bot.BotGet,
            status_code=status.HTTP_200_OK)
def update_bot(
    id: int,
    bot_update: bot.BotUpdate,
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    db_bot = db.query(models.Bot).filter(models.Bot.bot_id == id).first()

    if not db_bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")

    for var, value in bot_update.dict().items():
        if value is not None:
            setattr(db_bot, var, value)

    db.commit()
    db.refresh(db_bot)
    return db_bot


@router.delete("/{id}", 
            summary="Delete bot by id",
            description="Delete bot by bot id",
            status_code=status.HTTP_204_NO_CONTENT)
def delete_bot(
    id: int,
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    bot = db.query(models.Bot).filter(models.Bot.bot_id == id).first()

    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")

    db.delete(bot)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)