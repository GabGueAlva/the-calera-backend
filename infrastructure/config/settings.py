from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database Configuration
    database_url: Optional[str] = None

    # The Things Stack Configuration
    tts_application_id: str
    tts_api_key: str
    tts_server_url: str = "https://eu1.cloud.thethings.network"
    tts_storage_integration_id: str

    # Twilio WhatsApp Configuration
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_whatsapp_number: str
    recipient_whatsapp_number: str

    # Application Configuration
    app_name: str = "Frost Prediction System"
    debug: bool = False

    # Model Configuration
    model_data_path: str = "./models"
    
    class Config:
        env_file = ".env"


settings = Settings()