from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    
    API_VERSION: str = "/api/v1"

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

    # Runpod credentials
    runpod_endpoint: str
    runpod_api_key: str

    # Eleventlabs
    eleventlabs_api_key: str
    
    class Config:
        env_file = ".env"


settings = Settings()

class Config:
    # Voice provider
    VOICE_PROVIDER_1: str = "eleventlabs"
    VOICE_PROVIDER_2: str = "azure"
    VOICE_PROVIDER_3: str = "aws"
    VOICE_PROVIDER_4: str = "gcp"

configs = Config()