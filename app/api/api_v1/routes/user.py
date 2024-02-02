from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
from app import models
from app.schemas import user
from app.database import get_db
import app.utils as utils
from app.auth import get_current_user

router = APIRouter(
    prefix="/user",
    tags=['User']
)


@router.post("/signup", 
            summary="Create a new user",
            description="Create a new user after Signup screen",
            response_model=user.UserGet,
            status_code=status.HTTP_201_CREATED)
def create_user(
    user: user.UserCreate,
    db: Session = Depends(get_db), 
):  
    new_user = models.User(**user.dict())

    new_user.dob = utils.format_dob(user.dob)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_user.dob = utils.format_dob_str(new_user.dob)
    return new_user


@router.get("/{id}", 
            summary="Get user information",
            description="Get user information by user_id",
            response_model=user.UserGet)
def get_user(
    id: str,
    db: Session = Depends(get_db), 
    user_id: Optional[str] = Depends(get_current_user)
):
    user = db.query(models.User).filter(models.User.user_id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.dob = utils.format_dob_str(user.dob)
    return user


@router.patch("/{id}", 
            summary="Update user information",
            description="Update user information by user_id",
            response_model=user.UserGet)
def update_user(
    id: str,
    user_update: user.UserUpdate,
    db: Session = Depends(get_db), 
    user_id: Optional[str] = Depends(get_current_user)
):
    db_user = db.query(models.User).filter(models.User.user_id == id).first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    for var, value in user_update.dict().items():
        if var == "dob" and value is not None:
            setattr(db_user, var, utils.format_dob(value))
        elif value is not None:
            setattr(db_user, var, value) 

    db.commit()
    db.refresh(db_user)
    db_user.dob = utils.format_dob_str(db_user.dob)
    return db_user