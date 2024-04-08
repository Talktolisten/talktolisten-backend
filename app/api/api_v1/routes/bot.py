from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy import func
from app import models
from app.schemas import bot
from app.database import get_db
from app.auth import get_current_user
from app.config import configs
from app.api.api_v1.engines.text.utils import UTILS, UtilsEngine
from app.api.api_v1.engines.image.base import ImageEngine

import time

router = APIRouter(
    prefix="/bot",
    tags=['Bot']
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


@router.post("/create_bot/generate", 
            summary="Generate greeting and short description",
            description="Generate greeting and short description when creating a new bot",
            status_code=status.HTTP_200_OK
            )
def generate_bot(
    bot_create: bot.BotGenerate,
    current_user: str = Depends(get_current_user)
):
    engine = UtilsEngine(
        character_name=bot_create.bot_name,
        character_description=bot_create.description,
        util=UTILS[0]
    )

    greeting, description = engine.process_response_util_0(engine.get_response())

    return {
        "greeting": greeting,
        "short_description": description
    }


@router.post("/create_bot/optimize_description", 
            summary="Optimize bot description from existing description",
            description="Optimize bot description from existing description when creating a new bot",
            status_code=status.HTTP_200_OK
            )
def optimize_bot(
    bot_optimize: bot.BotGenerate,
    current_user: str = Depends(get_current_user)
):
    engine = UtilsEngine(
        character_name=bot_optimize.bot_name,
        character_description=bot_optimize.description,
        util=UTILS[1]
    )

    optimized_description = engine.get_response()

    return optimized_description


@router.post("/create_bot/generate_img_prompt", 
            summary="Generate image promptfor character",
            description="Generate image prompt for character when creating a new bot",
            status_code=status.HTTP_200_OK
            )
def generate_img_prompt(
    bot_optimize: bot.BotGenerate,
    current_user: str = Depends(get_current_user)
):
    engine = UtilsEngine(
        character_name=bot_optimize.bot_name,
        character_description=bot_optimize.description,
        util=UTILS[2]
    )

    image_prompt = engine.get_response()

    return image_prompt


@router.post("/create_bot/optimize_img_prompt", 
            summary="Optimize image prompt for character",
            description="Optimize image prompt for character when creating a new bot",
            status_code=status.HTTP_200_OK
            )
def optimize_img_prompt(
    image_prompt: str,
    current_user: str = Depends(get_current_user)
):
    engine = UtilsEngine(
        image_prompt=image_prompt,
        util=UTILS[3]
    )

    optimized_prompt = engine.get_response()

    return optimized_prompt


@router.post("/create_bot/generate_image", 
            summary="Generate image from a prompt for character",
            description="Generate image from a prompt for character when creating a new bot",
            status_code=status.HTTP_200_OK
            )
def optimize_img_prompt(
    image_prompt: str,
    current_user: str = Depends(get_current_user)
):
    # engine = ImageEngine(
    #     image_prompt=image_prompt,
    #     provider=configs.IMAGE_PROVIDER_1
    # )

    # image_url = engine.get_image_response()

    time.sleep(10)
    image_url = "https://dalleproduse.blob.core.windows.net/private/images/2ea03e7b-53b7-4b9c-8c17-bee8159b3494/generated_00.png?se=2024-04-08T03%3A46%3A00Z&sig=bUiI8xx3w1YWI1pBV%2FEm7%2BQasVB%2B5vGfCh1A3qalmUA%3D&ske=2024-04-14T03%3A44%3A13Z&skoid=09ba021e-c417-441c-b203-c81e5dcd7b7f&sks=b&skt=2024-04-07T03%3A44%3A13Z&sktid=33e01921-4d64-4f8c-a055-5bdaffd5e33d&skv=2020-10-02&sp=r&spr=https&sr=b&sv=2020-10-02"

    return image_url


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


@router.post("/like/{bot_id}", 
            summary="User likes a bot",
            description="User likes a bot by bot id",
            status_code=status.HTTP_200_OK)
def likes_bot(
    bot_id: int,
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    
    bot_to_like = db.query(models.Bot).filter(models.Bot.bot_id == bot_id).first()
    
    if not bot_to_like:
        raise HTTPException(status_code=404, detail="Bot not found")

    existing_like = db.query(models.user_likes_bots).filter_by(
        user_id=current_user,
        bot_id=bot_id
    ).first()

    if existing_like:
        return Response(status_code=status.HTTP_200_OK)

    db.execute(
        models.user_likes_bots.insert().values(
            user_id=current_user,
            bot_id=bot_id
        )
    )
    db.commit()

    return Response(status_code=status.HTTP_200_OK)


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