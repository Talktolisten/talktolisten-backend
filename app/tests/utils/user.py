from typing import Dict

from sqlalchemy.orm import Session

from app.models import User
from app.schemas.user import UserCreate
from app.tests.utils.utils import random_email, random_lower_string
from app.utils import format_dob, format_dob_str

def create_random_user(db: Session) -> User:
    user_id = random_lower_string()
    username = random_lower_string()
    gmail = random_email()
    first_name = random_lower_string()
    last_name = random_lower_string()
    profile_picture = random_lower_string()
    dob = "12 / 12 / 1999"
    user_in = UserCreate(user_id=user_id,
                        username=username, 
                        gmail=gmail, 
                        first_name=first_name, 
                        last_name=last_name, 
                        profile_picture=profile_picture, 
                        dob=dob)
    
    user = User(**user_in.dict())
    user.dob = format_dob(user_in.dob)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user