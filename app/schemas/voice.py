from pydantic import BaseModel
from typing import Optional

from pydantic.types import conint


class VoiceGet(BaseModel):
    voice_id: int
    voice_name: str
    voice_description: Optional[str]
    gender: Optional[str]
    language: Optional[str]
    style: Optional[str]
    sample_url: str

    class Config:
        from_attributes = True

class VoiceCreate(BaseModel):
    voice_name: str
    voice_description: str
    gender: str
    language: Optional[str]
    style: Optional[str]
    created_by: str

    class Config:
        from_atributes = True

class VoiceUpdate(BaseModel):
    voice_name: Optional[str]
    voice_description: Optional[str]
    style: Optional[str]

    class Config:
        from_attributes = True