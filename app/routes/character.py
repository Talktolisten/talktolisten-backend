from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
from .. import models
from app.schemas import character
from ..database import get_db


router = APIRouter(
    prefix="/characters",
    tags=['Characters']
)

@router.get("/{userID}", response_model=List[character.BotGet])
def get_characters(
    userID: str,
    db: Session = Depends(get_db), 
):
    return db.query(models.Bot).filter(models.Bot.created_by == userID).all()


@router.post("/", response_model=character.BotCreate, status_code=status.HTTP_201_CREATED)
def create_character(
    bot_create: character.BotCreate,
    db: Session = Depends(get_db), 
):
    db_bot = models.Bot(**bot_create.dict())
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot


@router.patch("/{id}", response_model=character.BotUpdate)
def update_character(
    id: int,
    bot_update: character.BotUpdate,
    db: Session = Depends(get_db), 
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


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(
    id: int,
    db: Session = Depends(get_db), 
):
    bot = db.query(models.Bot).filter(models.Bot.bot_id == id).first()

    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")

    db.delete(bot)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)