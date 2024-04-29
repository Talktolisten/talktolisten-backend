from app.config import settings
import requests
import os
import azure.cognitiveservices.speech as speechsdk
from app.api.api_v1.engines.storage.azure import azure_storage
from app.config import configs
from app.models import Voice

class VoiceEngine():
    def __init__(self, text: str, voiceObject: Voice, message_id: int):
        self.text = text
        self.message_id = message_id
        self.voice_name = voiceObject.voice_name
        self.voice_endpoint = voiceObject.voice_endpoint
        self.voice_provider = voiceObject.voice_provider
        self.style = voiceObject.style

        if self.voice_provider == configs.VOICE_PROVIDER_1:
            self.responseEngine = self.ElventLabsEngine()
        elif self.voice_provider == configs.VOICE_PROVIDER_2:
            self.responseEngine = self.AzureEngine()

    def ElventLabsEngine(self, stability = 0.7, similarity_boost = 0.5, style = 0.2, use_speaker_boost = True):
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

            return f"{settings.azure_db_endpoint}/audio-messages/{self.message_id}.mp3"
        except Exception as e:
            return e
        
    def AzureEngine(self):
        self.voice_name = f"en-US-{self.voice_name.split()[0]}Neural"
        speech_config = speechsdk.SpeechConfig(subscription=settings.speech_key, region=settings.speech_region)
        speech_config.speech_synthesis_voice_name = self.voice_name
        speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Audio16Khz128KBitRateMonoMp3)


        ssml_text = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts' xml:lang='en-US'>
        <voice name='{self.voice_name}'>
            <mstts:express-as style='{self.style}'>
            {self.text}
            </mstts:express-as>
        </voice>
        </speak>
        """

        text = self.text

        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

        result = speech_synthesizer.speak_ssml_async(ssml_text).get()

        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(text))
            # Save the synthesized audio to file
            stream = speechsdk.AudioDataStream(result)
            audio_file_path = f'app/api/api_v1/dependency/temp_audio/{self.message_id}output_audio.mp3'

            stream.save_to_wav_file(audio_file_path)

            azure_storage.upload_blob(audio_file_path, 'audio-messages', f'{self.message_id}.mp3')

            os.remove(audio_file_path)

            return f"{settings.azure_db_endpoint}/audio-messages/{self.message_id}.mp3"
        
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
            
            return None
        
    def get_audio_response(self):
        return self.responseEngine