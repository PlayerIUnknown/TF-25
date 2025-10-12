import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # Supabase
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # AI Microservice
    AI_MICROSERVICE_URL = os.getenv('AI_MICROSERVICE_URL', 'http://localhost:5001/api/chat')
    
    # Groq API (for survey analysis)
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
    
    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 8000))
    DEBUG = FLASK_ENV == 'development'
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # SSL Verification (disabled for development)
    VERIFY_SSL = False
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        if not Config.SUPABASE_URL:
            raise ValueError("SUPABASE_URL is required")
        if not Config.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY is required")
