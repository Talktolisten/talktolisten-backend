from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
from .. import models
from app.schemas import explore
from ..database import get_db


router = APIRouter(
    prefix="/explore",
    tags=['Explore']
)


@router.get("/", 
            summary="Get all bots",
            description="Get all bots in the database",
            response_model=List[explore.ExploreBots])
def get_characters(
    db: Session = Depends(get_db), 
    limit: int = 20, 
    skip: int = 0, 
    search: Optional[str] = None,
    category: Optional[str] = None
):
    query = db.query(models.Bot)

    if category:
        query = query.filter(models.Bot.category == category)

    if search:
        query = query.filter(models.Bot.bot_name.contains(search))

    bots = query.offset(skip).limit(limit).all()
    return bots


@router.get("/{id}", response_model=explore.ExploreBots)
def get_character_by_id(
    id: int,
    db: Session = Depends(get_db), 
):
    bot = db.query(models.Bot).filter(models.Bot.bot_id == id).first()

    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")

    return bot