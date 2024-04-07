from pydantic import BaseModel
from typing import Optional

from pydantic.types import conint


class VoiceGet(BaseModel):
    voice_id: int
    voice_name: str
    voice_description: Optional[str]
    sample_url: str

    class Config:
        from_attributes = True

class VoiceCreate(BaseModel):
    voice_name: str
    voice_description: str
    created_by: str

    class Config:
        from_atributes = True

class VoiceUpdate(BaseModel):
    voice_name: Optional[str]
    voice_description: Optional[str]

    class Config:
        from_attributes = True