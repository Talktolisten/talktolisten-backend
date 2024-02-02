import firebase_admin
from firebase_admin import credentials, auth
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from app.config import settings

cred = credentials.Certificate(f"app/{settings.firebase_json_name}")
default_app = firebase_admin.initialize_app(cred)


def get_current_user(authorization: Optional[str] = Header(None)):
    if authorization is None or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = authorization.split('Bearer ')[1]
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
