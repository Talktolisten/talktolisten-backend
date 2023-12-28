from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/")
def create_article() -> JSONResponse:
    return JSONResponse(status_code=200,
                        content={"message": "success"})