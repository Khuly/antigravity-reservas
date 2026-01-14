"""
Configuración centralizada del sistema usando Pydantic Settings.
Lee variables de entorno desde archivo .env
"""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Configuración global de la aplicación.
    Todas las variables se cargan desde .env
    """
    
    # Meta App Configuration
    meta_app_id: str = Field(..., alias="META_APP_ID")
    meta_app_secret: str = Field(..., alias="META_APP_SECRET")
    meta_verify_token: str = Field(..., alias="META_VERIFY_TOKEN")
    
    # Instagram Configuration
    instagram_page_access_token: str = Field(..., alias="INSTAGRAM_PAGE_ACCESS_TOKEN")
    
    # Facebook Messenger Configuration
    messenger_page_access_token: str = Field(..., alias="MESSENGER_PAGE_ACCESS_TOKEN")
    
    # WhatsApp Cloud API Configuration
    whatsapp_business_account_id: str = Field(..., alias="WHATSAPP_BUSINESS_ACCOUNT_ID")
    whatsapp_phone_number_id: str = Field(..., alias="WHATSAPP_PHONE_NUMBER_ID")
    whatsapp_access_token: str = Field(..., alias="WHATSAPP_ACCESS_TOKEN")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./reservations.db", alias="DATABASE_URL")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    debug: bool = Field(default=True, alias="DEBUG")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="app.log", alias="LOG_FILE")
    
    # Webhook Base URL (ngrok/Cloudflare)
    webhook_base_url: str = Field(default="http://localhost:8000", alias="WEBHOOK_BASE_URL")
    
    # WhatsApp Agent Number (for notifications)
    agent_whatsapp_number: str = Field(..., alias="AGENT_WHATSAPP_NUMBER")
    
    # Meta API URLs
    graph_api_version: str = "v21.0"
    graph_api_base_url: str = "https://graph.facebook.com"
    
    @property
    def graph_api_url(self) -> str:
        """URL base de Graph API con versión"""
        return f"{self.graph_api_base_url}/{self.graph_api_version}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()
