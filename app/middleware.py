from fastapi import Request, status, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from app.models import BlockIP
from app.database import get_db

class BlockIPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        db = next(get_db())
        try:
            blocked_ip = db.query(BlockIP).filter(BlockIP.ip == client_ip).first()
            if blocked_ip:
                return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "Access denied"})
        finally:
            db.close()
        
        return await call_next(request)
