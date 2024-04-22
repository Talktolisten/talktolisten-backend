from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
from app import models
from app.schemas import voice
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(
    prefix="/voice",
    tags=['Voice']
)

@router.get("/", 
            summary="Get all voices",
            description="Get all voices",
            response_model=List[voice.VoiceGet])
def get_voice(
    skip: int = 0, 
    limit: Optional[int] = None, 
    search: Optional[str] = None, 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    query = db.query(models.Voice)

    if search:
        query = query.filter(models.Voice.voice_name.contains(search))

    voice = query.offset(skip).limit(limit).all()
    return voice


@router.get("/{id}", 
            summary="Get voice by id",
            description="Get voice by id",
            response_model=voice.VoiceGet)
def get_voice_by_id(
    id: int,
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    voice = db.query(models.Voice).filter(models.Voice.voice_id == id).first()

    if not voice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voice not found")

    return voice


@router.get("/user/{id}", 
            summary="Get voice by user id",
            description="Get voice that the user created by user id",
            response_model=List[voice.VoiceGet])
def get_voice_by_user_id(
    id: str,
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    voice = db.query(models.Voice).filter(models.Voice.created_by == id).all()

    if not voice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voice not found")

    return voice


@router.patch("/{id}", 
            summary="Update voice information by id",
            description="Update voice information by id",
            response_model=voice.VoiceGet)
def update_voice(
    id: int,
    voice_update: voice.VoiceUpdate,
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
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


@router.post("/", 
            summary="Create / Clone new voice",
            description="Clone new voice using EleventLabs",
            response_model=voice.VoiceGet,
            status_code=status.HTTP_201_CREATED)
def clone_voice(
    voice: voice.VoiceCreate,
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    voice = models.Voice(**voice.dict())
    voice.voice_endpoint = "voice_endpoint"
    voice.voice_provider = "eleventlabs"

    db.add(voice)
    db.commit()
    db.refresh(voice)
    return voice


@router.delete("/{id}", 
            summary="Delete voice by id",
            description="Delete voice by id",
            status_code=status.HTTP_204_NO_CONTENT)
def delete_voice(
    id: int,
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    voice = db.query(models.Voice).filter(models.Voice.voice_id == id).first()

    if not voice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voice not found")

    db.delete(voice)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)