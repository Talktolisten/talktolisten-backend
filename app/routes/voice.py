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

@router.get("/", 
            summary="Get all voices",
            description="Get all voices",
            response_model=List[voice.GetVoice])
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


@router.get("/{id}", 
            summary="Get voice by id",
            description="Get voice by id",
            response_model=voice.GetVoice)
def get_voice_by_id(
    id: int,
    db: Session = Depends(get_db), 
):
    voice = db.query(models.Voice).filter(models.Voice.voice_id == id).first()

    if not voice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voice not found")

    return voice


@router.get("/user/{id}", 
            summary="Get voice by user id",
            description="Get voice that the user created by user id",
            response_model=List[voice.GetVoice])
def get_voice_by_user_id(
    id: str,
    db: Session = Depends(get_db), 
):
    voice = db.query(models.Voice).filter(models.Voice.created_by == id).all()

    if not voice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voice not found")

    return voice


@router.patch("/{id}", 
            summary="Update voice information by id",
            description="Update voice information by id",
            response_model=voice.GetVoice)
def update_voice(
    id: int,
    voice_update: voice.VoiceUpdate,
    db: Session = Depends(get_db), 
):
    db_voice = db.query(models.Voice).filter(models.Voice.voice_id == id).first()

    if not db_voice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voice not found")

    for var, value in voice_update.dict().items():
        if value is not None:
            setattr(db_voice, var, value)

    db.commit()
    db.refresh(db_voice)
    return db_voice


@router.post("/", status_code=status.HTTP_201_CREATED)
def clone_voice(
    voice: voice.CloneVoice,
    db: Session = Depends(get_db), 
):
    #send to ML model
    #return new_voice
    return


@router.delete("/{id}", 
            summary="Delete voice by id",
            description="Delete voice by id",
            status_code=status.HTTP_204_NO_CONTENT)
def delete_voice(
    id: int,
    db: Session = Depends(get_db), 
):
    voice = db.query(models.Voice).filter(models.Voice.voice_id == id).first()

    if not voice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voice not found")

    db.delete(voice)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)