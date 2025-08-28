import os
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
env_path = os.path.join(os.path.dirname(__file__), 'app', '.env')
load_dotenv(dotenv_path=env_path)

class Config:
    # Use Railway's DATABASE_URL if available, otherwise fallback to SQLite
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        # Railway uses postgresql://, but SQLAlchemy needs postgresql://
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or os.environ.get('DATABASE_URI') or 'sqlite:///nichegen.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # API Keys - load from environment
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Rate limiting
    RATE_LIMIT_DEFAULT = 10  # requests per hour for free users
    RATE_LIMIT_PAID = 100    # requests per hour for paid users