from typing import List, Optional
import openai
from openai import AzureOpenAI
import google.generativeai as genai
from app import models
from app.config import settings, server_config, configs
class TextEngine:
    def __init__(self, 
                message_list: str, 
                character_name: str,
                character_description: str,
                temperature: float = 1,
                max_tokens: int = 128
                ):
        self.api_key_token = ""
        provider = server_config.TEXT_PROVIDER
        self.system_prompt = f"Embody the specified character, complete with their background, core traits, relationships, and goals. Use a distinct speaking style reflective of their unique personality and environment. Responses should be very short and natural, as if you were having actual and realistic conversation. Avoid lengthy introductions or explanations. Remember, you are in an ongoing conversation, so your responses should be contextually aware and maintain the flow of the dialogue. Sometime you may ask questions to the user to keep the conversation going, and keep the user engaged. Do not always answer the user's questions directly, but keep the conversation interesting and engaging. {configs.PROMPT_OPTIMIZATION}\n"
        message_list.reverse()

        joined_messages = "\n".join(message_list)
        self.prompt = f"""{self.system_prompt}\nCharacter name: {character_name}\nCharacter Definition: {character_description}\n\n\n{joined_messages}\nCharacter:"""

        self.temperature = temperature
        self.max_tokens = max_tokens

        if provider == "together":
            self.api_key_token = settings.together_api_key
            self.responseEngine = self.TogetherEngine()
        elif provider == "google":
            self.api_key_token = settings.google_api_key
            self.responseEngine = self.GoogleEngine()
        elif provider == "azure":
            self.api_key_token = settings.azure_text_api_key
            self.responseEngine = self.AzureEngine()

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

    def TogetherEngine(self):
        client = openai.OpenAI(
            api_key=self.api_key_token,
            base_url='https://api.together.xyz/v1',
        )

        chat_completion = client.chat.completions.create(
        messages=[
            {
            "role": "system",
            "content": self.system_prompt,
            },
            {
            "role": "user",
            "content": self.prompt,
            }
        ],

        max_tokens=self.max_tokens,
        temperature=self.temperature,
        model="mistralai/Mixtral-8x7B-Instruct-v0.1"
        )

        return chat_completion.choices[0].message.content
    
    def get_response(self):
        return self.responseEngine
    
    
    def AzureEngine(self):
        client = AzureOpenAI(
            azure_endpoint = settings.azure_text_endpoint, 
            api_key=self.api_key_token,  
            api_version="2024-02-15-preview"
            )
        
        messages=[
            {
            "role": "system",
            "content": self.system_prompt,
            },
            {
            "role": "user",
            "content": self.prompt,
            }
        ]
        
        completion = client.chat.completions.create(
            model="ttl-gpt",
            messages = messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
            )

        return completion.choices[0].message.content
        

class GroupChatTextEngine:
    def __init__(self, 
                message_list: List[dict],
                all_bots: List[models.Bot],
                random_bot_name: str,
                temperature: float = 1,
                max_tokens: int = 128
                ):
        self.api_key_token = ""
        provider = server_config.TEXT_PROVIDER
        self.system_prompt = f"Embody the specified character, complete with their background, core traits, relationships, and goals. Use a distinct speaking style reflective of their unique personality and environment. Responses should be very short and natural, as if you were having actual and realistic conversation. Avoid lengthy introductions or explanations. Remember, you are in an ongoing conversation, so your responses should be contextually aware and maintain the flow of the dialogue. Sometime you may ask questions to the user to keep the conversation going, and keep the user engaged. Do not always answer the user's questions directly, but keep the conversation interesting and engaging. {configs.PROMPT_OPTIMIZATION}. Embody the character specified at the end of this prompt. Continue the conversation from the perspective of this character. This turn the character is {random_bot_name}\n"
        message_list.reverse()

        self.prompt = self.system_prompt + "All characters are in the group chat with user:\n\n"
        for bot in all_bots:
            self.prompt += f"{bot.bot_name}: {bot.description}\n"
        self.prompt += "\n\nLast 6 messages in the group chat (This can be None if this is the first message):\n\n"
        for message_object in message_list:
            if message_object['bot_name']:
                self.prompt += f"{message_object['bot_name']}: {message_object['message']}\n"
            else:
                self.prompt += f"User: {message_object['message']}\n"

        self.prompt += f"\n{random_bot_name}: "
        
        self.temperature = temperature
        self.max_tokens = max_tokens

        if provider == "together":
            self.api_key_token = settings.together_api_key
            self.responseEngine = self.TogetherEngine()
        elif provider == "google":
            self.api_key_token = settings.google_api_key
            self.responseEngine = self.GoogleEngine()
        elif provider == "azure":
            self.api_key_token = settings.azure_text_api_key
            self.responseEngine = self.AzureEngine()

    def get_response(self):
        return self.responseEngine
    

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

    def TogetherEngine(self):
        client = openai.OpenAI(
            api_key=self.api_key_token,
            base_url='https://api.together.xyz/v1',
        )

        chat_completion = client.chat.completions.create(
        messages=[
            {
            "role": "system",
            "content": self.system_prompt,
            },
            {
            "role": "user",
            "content": self.prompt,
            }
        ],

        max_tokens=self.max_tokens,
        temperature=self.temperature,
        model="mistralai/Mixtral-8x7B-Instruct-v0.1"
        )

        return chat_completion.choices[0].message.content
    

    def AzureEngine(self):
        client = AzureOpenAI(
            azure_endpoint = settings.azure_text_endpoint, 
            api_key=self.api_key_token,  
            api_version="2024-02-15-preview"
            )
        
        messages=[
            {
            "role": "system",
            "content": self.system_prompt,
            },
            {
            "role": "user",
            "content": self.prompt,
            }
        ]
        
        completion = client.chat.completions.create(
            model="ttl-gpt",
            messages = messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None
            )

        return completion.choices[0].message.content