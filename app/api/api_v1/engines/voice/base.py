from app.config import settings
import requests
import os
from app.api.api_v1.engines.storage.azure import azure_storage

class VoiceEngine():
    def __init__(self, text: str, voice_endpoint: str, message_id: int):
        self.text = text
        self.voice_endpoint = voice_endpoint
        self.message_id = message_id

    def get_audio_response_eleventlabs(self, stability = 0.7, similarity_boost = 0.5, style = 0.2, use_speaker_boost = True):
        voice_id = self.voice_endpoint.split("/")[-1]
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        payload = {
            "model_id": "eleven_turbo_v2",
            "text": self.text,
        }

        headers = {
            "xi-api-key": settings.eleventlabs_api_key,
            "Content-Type": "application/json"
        }

        try:
            response = requests.request("POST", url, json=payload, headers=headers)

            audio_file_path = f'app/api/api_v1/dependency/temp_audio/{self.message_id}output_audio.mp3'

            with open(audio_file_path, 'wb') as f:
                f.write(response.content)

            azure_storage.upload_blob(audio_file_path, 'audio-messages', f'{self.message_id}.mp3')

            os.remove(audio_file_path)

            return f"https://ttl.blob.core.windows.net/audio-messages/{self.message_id}.mp3"
        except Exception as e:
            return e