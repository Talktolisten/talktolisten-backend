from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
from app import models
from app.schemas import explore
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
    bots = db.query(models.Bot).filter(models.Bot.bot_name.contains(search)).offset(skip).limit(limit).all()
    return bots

@router.get("/category", 
            summary="Get bots by category",
            description="Get bots by category in the database",
            response_model=List[explore.ExploreBots])
def get_bots_by_category(
    category: str,
    limit: int = 20, 
    skip: int = 0, 
    current_user: dict= Depends(get_current_user),
    db: Session = Depends(get_db), 
):
    bots = db.query(models.Bot).filter(models.Bot.category == category).offset(skip).limit(limit).all()
    return bots


@router.get("/{id}", response_model=explore.ExploreBots)
def get_bot_by_id(
    id: int,
    current_user: dict= Depends(get_current_user),
    db: Session = Depends(get_db), 
):
    bot = db.query(models.Bot).filter(models.Bot.bot_id == id).first()

    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")

    return bot