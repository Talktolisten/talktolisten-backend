from openai import AzureOpenAI
import json
from app.config import settings, configs, server_config

class ImageEngine:
    def __init__(self, 
                image_prompt: str,
                provider: str = configs.IMAGE_PROVIDER_1
                ):
        self.image_prompt = image_prompt
        self.api_key_token = None

        if provider == configs.IMAGE_PROVIDER_1:
            self.api_key_token = settings.azure_img_api_key
            self.responseEngine = self.AzureEngine()

    def AzureEngine(self):
        client = AzureOpenAI(
            api_version="2024-02-01",
            azure_endpoint=settings.azure_img_endpoint,
            api_key=self.api_key_token,
        )
        try: 
            result = client.images.generate(
                model=server_config.IMAGE_ENDPOINT_NAME,
                prompt=self.image_prompt,
                n=1
            )
        except Exception as e:
            print(f"Error: {e}")
            return None

        image_url = json.loads(result.model_dump_json())['data'][0]['url']
        return image_url

    def get_image_response(self):
        return self.responseEngine