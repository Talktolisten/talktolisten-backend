from app.config import settings
from typing import List
import requests
from pydub import AudioSegment
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import requests
from io import BytesIO
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


def create_group_profile_picture(avatar_paths, output_size=(1024, 1024)):
    
    def mask_circle_transparent(im, blur_radius, offset=0):
        offset = blur_radius * 2 + offset
        mask = Image.new("L", im.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((offset, offset, im.size[0] - offset, im.size[1] - offset), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

        result = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
        result.putalpha(mask)
        return result
    
    images = []

    for url in avatar_paths:
        response = requests.get(url)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            image = image.resize((output_size[0] // 2, output_size[1] // 2), Image.Resampling.LANCZOS)
            image = mask_circle_transparent(image, 0)
            images.append(image)
    base_image = Image.new('RGBA', output_size, (255, 255, 255, 0))


    if len(images) == 2:
        new_width = output_size[0] // 2
        new_height = new_width 
        images = [im.resize((new_width, new_height), Image.Resampling.LANCZOS) for im in images]
        images = [mask_circle_transparent(im, 0) for im in images]
        base_image.paste(images[0], (0, (output_size[1] - new_height) // 2), images[0])
        base_image.paste(images[1], (new_width, (output_size[1] - new_height) // 2), images[1])

    elif len(images) == 3:
        new_width = output_size[0] // 2
        new_height = new_width  
        resized_images = [im.resize((new_width, new_height), Image.Resampling.LANCZOS) for im in images[:2]]
        resized_images = [mask_circle_transparent(im, 0) for im in resized_images]
        third_img = images[2].resize((new_width, new_height), Image.Resampling.LANCZOS)
        third_img = mask_circle_transparent(third_img, 0)

        base_image.paste(resized_images[0], (0, 0), resized_images[0])
        base_image.paste(resized_images[1], (new_width, 0), resized_images[1])
        base_image.paste(third_img, ((output_size[0] - new_width) // 2, new_height), third_img)

    elif len(images) == 4:
        new_width = output_size[0] // 2
        new_height = new_width
        resized_images = [im.resize((new_width, new_height), Image.Resampling.LANCZOS) for im in images]
        resized_images = [mask_circle_transparent(im, 0) for im in resized_images]
        base_image.paste(resized_images[0], (0, 0), resized_images[0])
        base_image.paste(resized_images[1], (new_width, 0), resized_images[1])
        base_image.paste(resized_images[2], (0, new_height), resized_images[2])
        base_image.paste(resized_images[3], (new_width, new_height), resized_images[3])

    return base_image