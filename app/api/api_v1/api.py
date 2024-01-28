from fastapi import APIRouter

from app.routes import character, explore, user, chat, voice

api_router = APIRouter()
api_router.include_router(explore.router)
api_router.include_router(character.router)
api_router.include_router(user.router)
api_router.include_router(voice.router)
api_router.include_router(chat.router)