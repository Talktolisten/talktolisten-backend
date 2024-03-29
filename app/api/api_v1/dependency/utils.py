from app.config import settings
from typing import List
import requests
from pydub import AudioSegment
import os
import wave
import asyncio
import base64
from app.models import Message

def decode_base64(base64_string):
    return base64.b64decode(base64_string)

def convert_m4a_to_wav(input_file, output_file):
    audio = AudioSegment.from_file(input_file, format="m4a")
    audio.export(output_file, format="wav")

def save_wav(input, output):
    """Saves the wav file which needs to be concatenated with the audio."""
    with open(input, 'rb') as wav_file:
        audio = wav_file.read()
        with open(output, 'wb') as output_file:
            output_file.write(audio)

def concatenate_wav_files(input_file_paths, chat_id):
    if not input_file_paths:
        print('no')
    output_filename = f'app/api/api_v1/dependency/temp_audio/{chat_id}audio_to_translate.wav'
    params = None

    # Open the first input file and get its parameters
    print('here')
    with wave.open(input_file_paths[0], 'rb') as first_input_wav:
        params = first_input_wav.getparams()

    # Open the output file with the parameters of the first input file
    with wave.open(output_filename, 'wb') as output_wav:
        output_wav.setparams(params)
        print(input_file_paths)
        for input_filename in input_file_paths:
            print(input_filename)
            with wave.open(input_filename, 'rb') as input_wav:
                # Check if the parameters of the current input file match the parameters of the first input file
                assert input_wav.getparams() == params, "Input files have different parameters"
                output_wav.writeframes(input_wav.readframes(input_wav.getnframes()))

    return output_filename

def azure_speech_to_text(audio_path):
    try:
        headers = {
            "Ocp-Apim-Subscription-Key": settings.speech_key,
            "Content-Type": "audio/wav"
        }

        url = f"https://{settings.speech_region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=en-US&format=detailed"
        audio_file = open(audio_path, 'rb')
        response = requests.post(url, headers=headers, data=audio_file)

        response.raise_for_status()

        return response.json().get("DisplayText")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
def get_ml_response(system, prompt):
    try:
        headers = {
            "Authorization": f"Bearer {settings.runpod_api_key}",
        }
        url = f"https://api.runpod.ai/v2/{settings.runpod_endpoint}/run"
        data = {
            "input": {
                "system": system,
                "prompt": prompt
            },
            "temperature": 0.9
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        job_id = response.json().get("id")
        return job_id
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
def extract_ml_answer(ml_response):
    start_index = ml_response.find("[/INST]")
    start_index += 8
    end_index = start_index+7
    while end_index < len(ml_response) and ml_response[end_index]!= "]" and ml_response[end_index]!= "\n":
        end_index += 1
    rest_of_string = ml_response[start_index : end_index].replace("\n", "")
    return rest_of_string


async def check_ml_response(job_id):
    try:
        headers = {
            "Authorization": f"Bearer {settings.runpod_api_key}",
        }
        url = f"https://api.runpod.ai/v2/{settings.runpod_endpoint}/status/{job_id}"

        MAX_TRIES = 10
        SLEEP_TIME = 1.5
        for _ in range(MAX_TRIES):
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            status = response.json().get("status")
            if status == "COMPLETED":
                print(response.json().get("output").get("output"))
                response = extract_ml_answer(response.json().get("output").get("output"))
                print(response)
                return response
            else:
                await asyncio.sleep(SLEEP_TIME)
        return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
def make_message_lists(message_list: List[Message]) -> list:
    messages = []
    for message in message_list:
        if message.is_bot:
            messages.append("Character: " + message.message)
        else:
            messages.append("User: " + message.message)
    return messages