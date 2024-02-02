from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    
    API_VERSION: str = "/api/v1"

    firebase_json_name: str
    
    class Config:
        env_file = ".env"


settings = Settings()