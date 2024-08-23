from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    
    API_VERSION: str = "/api/v1"

    developer_email: str
    sendgrid_api_key: str

    admin_id: str

    #Firebase credentials
    fb_type: str
    fb_project_id: str
    fb_private_key_id: str
    fb_private_key: str
    fb_client_email: str
    fb_client_id: str
    fb_auth_uri: str
    fb_token_uri: str
    fb_auth_provider_x509_cert_url: str
    fb_client_x509_cert_url: str
    fb_universe_domain: str
    
    # Azure credentials
    speech_key: str
    speech_region: str
    azure_text_api_key: str
    azure_text_endpoint: str
    azure_img_api_key: str
    azure_img_endpoint: str
    azure_connection_string: str
    azure_db_endpoint: str

    # Runpod credentials
    runpod_endpoint: str
    runpod_api_key: str

    # Eleventlabs
    eleventlabs_api_key: str

    # Text provider
    together_api_key: str
    google_api_key: str

    class Config:
        env_file = ".env"


settings = Settings()

class Config:
    # Voice provider
    VOICE_PROVIDER_1: str = "eleventlabs"
    VOICE_PROVIDER_2: str = "azure"
    VOICE_PROVIDER_3: str = "aws"
    VOICE_PROVIDER_4: str = "gcp"

    # Text provider
    TEXT_PROVIDER_1: str = "together"
    TEXT_PROVIDER_2: str = "google"
    TEXT_PROVIDER_3: str = "azure"

    # Image provider
    IMAGE_PROVIDER_1: str = "azure"
    IMAGE_PROVIDER_2: str = "openai"
    IMAGE_PROVIDER_3: str = "google"
    IMAGE_PROVIDER_4: str = "deepai"

    # Image modals
    IMAGE_ENDPOINT_NAME_1 = "Dalle3"
    IMAGE_ENDPOINT_NAME_2 = "Dalle3-2"

    # Prompt Optimization for third party LLM
    PROMPT_OPTIMIZATION = "Provide a response that is easy to understand and communicate effectively with the user. Use clear, direct language and aim for a Flesch reading score of 80 or higher. Avoid complex terminology, technical jargon, and excessive adverbs or buzzwords. Only use relevant domain-specific jargon when necessary to provide a complete explanation"

configs = Config()


class ServerConfig:
    # Server config
    server = os.getenv("SERVER")
    if server == "1":
        TEXT_PROVIDER = configs.TEXT_PROVIDER_2
        IMAGE_ENDPOINT_NAME = configs.IMAGE_ENDPOINT_NAME_1
    else:
        TEXT_PROVIDER = configs.TEXT_PROVIDER_3
        IMAGE_ENDPOINT_NAME = configs.IMAGE_ENDPOINT_NAME_2

server_config = ServerConfig()