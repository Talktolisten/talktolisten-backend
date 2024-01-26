from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
from .. import models
from app.schemas import voice
from ..database import get_db

router = APIRouter(
    prefix="/voice",
    tags=['Voice']
)

@router.get("/", response_model=List[voice.GetVoice])
def get_voice(
    db: Session = Depends(get_db),
    limit: int = 25, 
    skip: int = 0, 
    search: Optional[str] = None 
):
    query = db.query(models.Voice)

    if search:
        query = query.filter(models.Voice.voice_name.contains(search))

    voice = query.offset(skip).limit(limit).all()
    return voice


@router.post("/", status_code=status.HTTP_201_CREATED)
def clone_voice(
    voice: voice.CloneVoice,
    db: Session = Depends(get_db), 
):
    #send to ML model
    #return new_voice
    return

