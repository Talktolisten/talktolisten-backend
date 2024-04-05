import openai
import google.generativeai as genai
from app.config import settings
class TextEngine:
    def __init__(self, 
                message_list: str, 
                character_name: str,
                character_description: str,
                provider: str,
                temperature: float = 1,
                max_tokens: int = 128
                ):
        self.api_key_token = ""

        self.system_prompt = "Embody the specified character, complete with their background, core traits, relationships, and goals. Use a distinct speaking style reflective of their unique personality and environment. Responses should be very short and natural, as if you were having actual and realistic conversation. Avoid lengthy introductions or explanations. Remember, you are in an ongoing conversation, so your responses should be contextually aware and maintain the flow of the dialogue."
        message_list.reverse()

        joined_messages = "\n".join(message_list)
        self.prompt = f"""{self.system_prompt}\nCharacter name: {character_name}\nCharacter Definition: {character_description}\n\n\n{joined_messages}\nCharacter:"""

        self.temperature = temperature
        self.max_tokens = max_tokens

        if provider == "together":
            self.api_key_token = settings.together_api_key
            self.responseEngine = self.TogetherEngine()
        
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
        