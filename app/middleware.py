from fastapi import Request, status, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from app.models import BlockIP
from app.database import get_db
from app.config import settings 

allowed_paths = [
    "/",
    "/redoc",
    "/docs",
    "/openapi.json",
    "/favicon.ico",
    "/robots.txt",
    "/sitemap.xml"
]

class BlockIPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        db = next(get_db())
        try:
            blocked_ip = db.query(BlockIP).filter(BlockIP.ip == client_ip).first()
            if blocked_ip or not (request.url.path in allowed_paths or request.url.path.startswith(settings.API_VERSION)):
                return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "Access denied"})
        finally:
            db.close()
        
        return await call_next(request)
