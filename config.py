import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'fieldbuddy')
    
    # API Keys
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '')
    DATA_GOV_API_KEY = os.getenv('DATA_GOV_API_KEY', '')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    
    # File Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    IMAGES_DIR = os.path.join(BASE_DIR, 'images')
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    
    # Application Settings
    APP_NAME = "FieldBuddy"
    APP_VERSION = "1.0.0"
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'fieldbuddy.log')
    
    # Cache Settings
    CACHE_ENABLED = True
    CACHE_TTL = 3600  # 1 hour in seconds
    
    # Security Settings
    PASSWORD_HASH_ALGORITHM = 'bcrypt'
    SESSION_TIMEOUT = 3600  # 1 hour in seconds
    
    @classmethod
    def get_database_url(cls):
        return f"mysql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}/{cls.DB_NAME}"
    
    @classmethod
    def get_image_path(cls, filename):
        return os.path.join(cls.IMAGES_DIR, filename)
    
    @classmethod
    def get_data_path(cls, filename):
        return os.path.join(cls.DATA_DIR, filename) 