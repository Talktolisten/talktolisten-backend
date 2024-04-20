from fastapi import APIRouter

from app.api.api_v1.routes import bot, explore, user, chat, voice, groupchat

api_router = APIRouter()
api_router.include_router(explore.router)
api_router.include_router(bot.router)
api_router.include_router(user.router)
api_router.include_router(voice.router)
api_router.include_router(chat.router)
api_router.include_router(groupchat.router)