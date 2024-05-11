from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from app.api.api_v1.api import api_router
from app.config import settings, server_config
from app.middleware import BlockIPMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Talk To Listen", version="1.0.0", description="Talk To Listen API Documentation. Only for showcase purpose.", redoc_url="/redoc")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization"],
)

app.add_middleware(BlockIPMiddleware)

@app.get("/")
def talk_to_listen():
    return {"message": f"Talk To Listen BackEnd. Server: {server_config.server}"}

app.include_router(api_router, prefix=settings.API_VERSION)