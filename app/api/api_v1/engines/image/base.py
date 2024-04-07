from openai import AzureOpenAI
import json
from app.config import settings, configs

class ImageEngine:
    def __init__(self, 
                image_prompt: str,
                provider: str = configs.IMAGE_PROVIDER_1
                ):
        self.image_prompt = image_prompt
        self.api_key_token = None

        if provider == configs.IMAGE_PROVIDER_1:
            self.api_key_token = settings.azure_api_key
            self.responseEngine = self.AzureEngine()

    def AzureEngine(self):
        client = AzureOpenAI(
            api_version="2024-02-01",
            azure_endpoint="https://ttl-image-gen.openai.azure.com/",
            api_key=self.api_key_token,
        )

        result = client.images.generate(
            model="Dalle3",
            prompt=self.image_prompt,
            n=1
        )

        image_url = json.loads(result.model_dump_json())['data'][0]['url']
        return image_url

    def get_image_response(self):
        return self.responseEngine