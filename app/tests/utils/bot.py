from typing import Dict, Optional
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Bot
from app.schemas.bot import BotCreate
from app.tests.utils.utils import random_lower_string
from app.tests.utils.user import create_random_user
from app.tests.utils.voice import create_random_voice


def create_random_bot(db: Session, 
                    owner_id: Optional[str] = None,
                    bot_name: Optional[str] = None,
                    category: Optional[str] = None) -> Bot:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.user_id
    
    voice = create_random_voice(db, owner_id)

    bot_name = random_lower_string()
    short_description = random_lower_string()
    description = random_lower_string()
    profile_picture = random_lower_string()
    category = random_lower_string()
    voice_id = voice.voice_id
    created_by = owner_id
    bot_in = BotCreate(bot_name=bot_name,
                        short_description=short_description, 
                        description=description, 
                        profile_picture=profile_picture, 
                        category=category, 
                        voice_id=voice_id, 
                        created_by=created_by)
    bot = Bot(**bot_in.dict())
    
    db.add(bot)
    db.commit()
    db.refresh(bot)
    return bot