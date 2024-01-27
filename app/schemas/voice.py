from pydantic import BaseModel
from typing import Optional

from pydantic.types import conint


class GetVoice(BaseModel):
    voice_id: int
    voice_name: str
    voice_description: Optional[str]

    class Config:
        from_attributes = True

class CloneVoice(BaseModel):
    voice_id: int
    voice_name: str
    voice_description: Optional[str]
    voice_provider: str     #string from mp3 file
    created_by: str


    class Config:
        from_atributes = True

class VoiceUpdate(BaseModel):
    voice_name: Optional[str]
    voice_description: Optional[str]

    class Config:
        from_attributes = True