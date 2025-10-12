import os
import ssl

# Ensure SSL is disabled
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

from supabase import create_client, Client
from config import Config


class Database:
    """Supabase database client wrapper"""
    
    _client: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client"""
        if cls._client is None:
            # Create client
            cls._client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        return cls._client
    
    @classmethod
    def init_app(cls, app=None):
        """Initialize database with Flask app"""
        Config.validate()
        cls.get_client()
        if app:
            app.logger.info("Supabase connection established")


# Convenience function
def get_db() -> Client:
    """Get database client instance"""
    return Database.get_client()

