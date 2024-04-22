import openai
import google.generativeai as genai
from app.config import settings, server_config, configs


UTILS = [
    "greetings and short description",
    "optimize description",
    "generate image prompt",
    "optimize image prompt"
]

class UtilsEngine():
    def __init__(self, 
                character_name: str = None,
                character_description: str = None,
                image_prompt: str = None,
                temperature: float = 1,
                max_tokens: int = 512,
                util: str = None
                ):
        self.temperature = temperature
        self.max_tokens = max_tokens
        provider = "google"
        if util == UTILS[0]:
            self.prompt = f"You are tasked with crafting a greeting AND a concise description for the specified character. The greeting should use a distinct speaking style reflective of their unique personality, while the short description should encapsulate the character's key traits in a few words, based on the provided description. Ensure the response is short, natural, and directly relevant to the character's name and definition. You must only response with the greeting and the short description. {configs.PROMPT_OPTIMIZATION}. The response should be EXACTLY structured as follows:\nGreeting: [Your greeting here]\nShort Description: [Your description here]\n\nCharacter name: {character_name}\nCharacter Definition: {character_description}"
        elif util == UTILS[1]:
            self.prompt = f"Given the following character description, your task is to refine and enhance it. Make it more specific, detailed, and vivid, but keep your response SHORT, NATURAL, concise and stick with the origin. Use descriptive language to bring the character to life, and ensure the revised description captures the essence of the character's personality, background, and key traits in as few words as possible. {configs.PROMPT_OPTIMIZATION}\n\nCharacter name: {character_name}\nCharacter Definition: {character_description}"
        elif util == UTILS[2]:
            self.prompt = f"Generate an image prompt that visually represents the character based on the provided description. The image prompt should capture the character's key traits, personality, and background in a vivid and imaginative way. Remember, the goal is to create a SHORT prompt that would inspire an ai image generator to create an image that accurately represents the character.\n\nCharacter name: {character_name}\nCharacter Definition: {character_description}"
        elif util == UTILS[3]:
            self.prompt = f"Given the following image prompt, your task is to refine and enhance it. Make it more specific, detailed, and vivid, but keep your response short and natural. Use descriptive language to bring the character to life, and ensure the revised prompt captures the essence of the character's personality, background, and key traits in as few words as possible. The goal is to inspire an artist to create an image that accurately represents the character.\n\nImage Prompt: {image_prompt}"

        if provider == "google":
            self.api_key_token = settings.google_api_key
            self.responseEngine = self.GoogleEngine()


    def GoogleEngine(self):
        genai.configure(api_key=self.api_key_token)

        generation_config = {
            "temperature": self.temperature,
            "top_p": 1,
            "top_k": 50,
            "max_output_tokens": self.max_tokens,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH"
            }
        ]

        model = genai.GenerativeModel(model_name="gemini-pro",
                                    generation_config=generation_config,
                                    safety_settings=safety_settings)

        responses = model.generate_content(self.prompt)
        return responses.text
    
    def get_response(self):
        return self.responseEngine
    
    def process_response_util_0(self, response):
        print(response)
        greeting = response.split("\n")[0].replace("Greeting: ", "")
        description = response.split("\n")[1].replace("Short Description: ", "")
        return greeting, description