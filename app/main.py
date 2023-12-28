import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(auth.router)  # username:PK, dob, fname,uid store in postgres -> uid(firebase) : PK


@app.get("/")
def root():
    return {"message": "Talk To Listen BackEnd"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8088, log_level='debug')