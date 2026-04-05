"""Configuración del proyecto"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = "mi_api"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

settings = Settings()
