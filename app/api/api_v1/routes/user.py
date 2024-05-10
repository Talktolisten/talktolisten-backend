from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from PIL import Image
import io
import os
import uuid

from sqlalchemy import func
from app import models
from app.schemas import user, bot
from app.database import get_db
import app.utils as utils
from app.config import settings
from app.auth import get_current_user
from app.api.api_v1.engines.storage.azure import azure_storage
from app.api.api_v1.dependency.utils import decode_base64

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


@router.get("/check_user_exists/{user_id}", 
            summary="Check if a user exists",
            description="Check if a user exists in the database",
            response_model=bool)
def check_user_exists(
    user_id: str,
    db: Session = Depends(get_db), 
):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()

    return user is not None


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
        elif value is not None and var != "profile_picture":
            setattr(db_user, var, value) 

    db.commit()

    if user_update.profile_picture is not None:
        image_path = f"app/api/api_v1/dependency/temp_img_{user_id}.webp"
        image_url = user_update.profile_picture
        image_data = decode_base64(image_url)
        image = Image.open(io.BytesIO(image_data))
        image.save(image_path, 'WEBP')

        image_upload = f"{user_id}.webp"

        azure_storage.delete_blob("user-avatar", image_upload)

        azure_storage.upload_blob(image_path, "user-avatar", image_upload)

        db_user.profile_picture = f"{settings.azure_db_endpoint}/user-avatar/{image_upload}"

        os.remove(image_path)
        
    db.commit()
    db.refresh(db_user)
    db_user.dob = utils.format_dob_str(db_user.dob)
    return db_user


@router.delete("/{id}",
            summary="Delete user by id",
            description="Delete user by user_id",
            status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    id: str,
    db: Session = Depends(get_db), 
    user_id: Optional[str] = Depends(get_current_user)
):
    user = db.query(models.User).filter(models.User.user_id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/check_username/{username}", 
            summary="Check if a username exists",
            description="Check if a username exists in the database",
            response_model=bool)
def check_username(
    username: str,
    db: Session = Depends(get_db), 
):
    user = db.query(models.User).filter(models.User.username == username).first()

    return user is not None


@router.get("/created_bots", 
            summary="Get all bots created by users",
            description="Get all bots created by users by user_id",
            response_model=bot.BotGet)
def get_created_bots(
    db: Session = Depends(get_db), 
    user_id: Optional[str] = Depends(get_current_user)
):  
    bots = db.query(models.Bot).filter(models.Bot.created_by == user_id).all()
    return bots


@router.post("/feedback_report",
            summary="Send feedback or report",
            description="Send feedback or report to the developers",
            status_code=status.HTTP_201_CREATED)
def send_fr(
    FeedbackReportObj: user.FeedbackReport,
    db: Session = Depends(get_db), 
    user_id: Optional[str] = Depends(get_current_user)
):  
    img_list = []
    if FeedbackReportObj.pictures is not None:
        for i in range(len(FeedbackReportObj.pictures)):
            temporary_id = uuid.uuid4()
            image_path = f"app/api/api_v1/dependency/temp_img_rf_{temporary_id}.webp"
            image_url = FeedbackReportObj.pictures[i]
            image_data = decode_base64(image_url)
            image = Image.open(io.BytesIO(image_data))
            image.save(image_path, 'WEBP')

            image_upload = f"{temporary_id}.webp"

            azure_storage.upload_blob(image_path, "feedback-report", image_upload)
            img_list.append(f"{settings.azure_db_endpoint}/feedback-report/{image_upload}")
            os.remove(image_path)
    
    if FeedbackReportObj.feedback is not None:
        utils.send_email("Feedback", FeedbackReportObj.feedback, img_list)
    else:
        utils.send_email("Report", FeedbackReportObj.report, img_list)

    db_fr = models.FeedbackReport(feedback = FeedbackReportObj.feedback, report = FeedbackReportObj.report, user_id = user_id, pictures = img_list)

    db.add(db_fr)
    db.commit()
    db.refresh(db_fr)

    return Response(status_code=status.HTTP_201_CREATED)