from typing import Dict, Optional
from sqlalchemy.orm import Session

from app.models import Voice
from app.schemas.voice import VoiceCreate
from app.tests.utils.utils import random_email, random_lower_string
from app.tests.utils.user import create_random_user


def create_random_voice(db: Session, owner_id: Optional[str] = None) -> Voice:
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.user_id

    voice_name = random_lower_string()
    voice_description = random_lower_string()
    created_by = owner_id
    voice_in = VoiceCreate(voice_name=voice_name,
                        voice_description=voice_description,
                        created_by=created_by)
    
    voice = Voice(**voice_in.dict())
    voice.voice_endpoint = "voice_endpoint"
    voice.voice_provider = "eleventlabs"

    db.add(voice)
    db.commit()
    db.refresh(voice)
    return voice