from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
from .. import models
from app.schemas import user
from ..database import get_db
import app.utils as utils

router = APIRouter(
    prefix="/user",
    tags=['User']
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(
    user: user.UserCreate,
    db: Session = Depends(get_db), 
):  
    new_user = models.User(**user.dict())

    new_user.dob = utils.format_dob(user.dob)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{id}", response_model=user.UserGet)
def get_user(
    id: str,
    db: Session = Depends(get_db), 
):
    user = db.query(models.User).filter(models.User.user_id == id).first()
    user.dob = utils.format_dob_str(user.dob)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user