from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "WebChatAgents"
    PROJECT_DESCRIPTION: str = "API for analyzing websites"
    PROJECT_VERSION: str = "1.0.0"
    
    # API Security
    APP_API_KEY: str = os.getenv("APP_API_KEY", "your-secret-key-here")
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # OpenAI Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields in the model
        env_file_encoding = 'utf-8'
        env_nested_delimiter = '__'
        env_prefix = ''  # No prefix for environment variables

settings = Settings()