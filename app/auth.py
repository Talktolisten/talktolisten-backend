import firebase_admin
from firebase_admin import credentials, auth
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from app.config import settings

fb_credentials = {
  "type": settings.fb_type,
  "project_id": settings.fb_project_id,
  "private_key_id": settings.fb_private_key_id,
  "private_key": settings.fb_private_key.replace('\\n', '\n'),
  "client_email": settings.fb_client_email,
  "client_id": settings.fb_client_id,
  "auth_uri": settings.fb_auth_uri,
  "token_uri": settings.fb_token_uri,
  "auth_provider_x509_cert_url": settings.fb_auth_provider_x509_cert_url,
  "client_x509_cert_url": settings.fb_client_x509_cert_url,
  "universe_domain": settings.fb_universe_domain,
}

cred = credentials.Certificate(fb_credentials)
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
