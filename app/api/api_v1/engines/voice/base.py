from app.config import settings
import requests
import os
import base64

class VoiceEngine():
    def __init__(self, text: str, voice_endpoint: str):
        self.text = text
        self.voice_endpoint = voice_endpoint

    def get_audio_response_eleventlabs(self, stability = 0.7, similarity_boost = 0.5, style = 0.2, use_speaker_boost = True):
        voice_id = self.voice_endpoint.split("/")[-1]
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        payload = {
            "model_id": "eleven_turbo_v2",
            "text": self.text,
            "voice_settings": {
                "similarity_boost": similarity_boost,
                "stability": stability,
                "use_speaker_boost": True,
                "style": style
            }
        }

        headers = {
            "xi-api-key": settings.eleventlabs_api_key,
            "Content-Type": "application/json"
        }

        try:
            response = requests.request("POST", url, json=payload, headers=headers)

            audio_file_path = 'app/api/api_v1/dependency/temp_audio/output_audio.mp3'

            with open(audio_file_path, 'wb') as audio_file:
                audio_file.write(response.content)
            
            with open(audio_file_path, 'rb') as audio_file:
                audio = audio_file.read()  

            audio_base64 = base64.b64encode(audio).decode('utf-8')

            os.remove(audio_file_path)
            return audio_base64
        except Exception as e:
            return e