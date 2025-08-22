from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID", "")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    resend_api_key: str = os.getenv("RESEND_API_KEY", "")
    
    # Email Configuration
    spa_manager_email: str = os.getenv("SPA_MANAGER_EMAIL", "manager@yourspa.com")
    spa_name: str = os.getenv("SPA_NAME", "Luxury Spa & Wellness")
    spa_address: str = os.getenv("SPA_ADDRESS", "123 Wellness Street, City, State 12345")
    spa_phone: str = os.getenv("SPA_PHONE", "+1 (555) 123-4567")
    
    # Google Calendar & Sheets
    google_calendar_id: str = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    google_sheets_id: str = os.getenv("GOOGLE_SHEETS_ID", "")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./spa_automation.db")
    
    # AI Configuration
    ai_model: str = os.getenv("AI_MODEL", "gpt-3.5-turbo")
    max_tokens: int = int(os.getenv("MAX_TOKENS", "1000"))
    
    # Business Hours
    business_hours: dict = {
        "monday": {"open": "09:00", "close": "20:00"},
        "tuesday": {"open": "09:00", "close": "20:00"},
        "wednesday": {"open": "09:00", "close": "20:00"},
        "thursday": {"open": "09:00", "close": "20:00"},
        "friday": {"open": "09:00", "close": "20:00"},
        "saturday": {"open": "10:00", "close": "18:00"},
        "sunday": {"open": "10:00", "close": "16:00"}
    }
    
    # Appointment Settings
    appointment_duration: int = int(os.getenv("APPOINTMENT_DURATION", "60"))  # minutes
    buffer_time: int = int(os.getenv("BUFFER_TIME", "15"))  # minutes between appointments
    
    class Config:
        env_file = ".env"

settings = Settings()
