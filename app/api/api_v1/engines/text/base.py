import openai
from app.config import settings
class TextEngine:
    def __init__(self, 
                question: str, 
                character_name: str,
                character_description: str,
                provider: str,
                ):
        self.api_key_token = ""

        self.system_prompt = "Embody the specified character, complete with their background, core traits, relationships, and goals. Use a distinct speaking style reflective of their unique personality and environment and answer in short. Communicate using their distinct manner of speech, reflecting their unique personality and setting. Responses should be brief and omit direct self-reference by name, focusing solely on providing character-driven insights."

        self.prompt = f"""<character_name>{character_name}</s>\n
        <|character|>{character_description}</s>\n
        <|user|>{question}</s>\n
        <|response|>
        """

        self.temperature = 1.25
        self.max_tokens = 256

        if provider == "together":
            self.api_key_token = settings.together_api_key
            self.responseEngine = self.TogetherEngine()

    def TogetherEngine(self):
        print(self.api_key_token)
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
        