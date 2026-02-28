import os
from datetime import timedelta

class Config:
    """Application configuration"""

    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///gut_health.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # LLM Provider configurations
    OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'hf.co/MaziyarPanahi/phi-4-GGUF:latest')

    # OpenAI configuration (optional)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4')

    # Anthropic configuration (optional)
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
    ANTHROPIC_MODEL = os.environ.get('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')

    # Application settings
    ITEMS_PER_PAGE = 20
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # File upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_HTTPONLY = True

    # Template configuration - disable caching for development
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0

    # Admin mode - controls visibility of content management UI
    # Set ADMIN_MODE=true in environment to enable upload/edit/delete features
    ADMIN_MODE = os.environ.get('ADMIN_MODE', 'false').lower() == 'true'

    # External webhook secrets for HMAC signature validation
    # Empty = signature validation skipped (safe for development)
    EXTERNAL_WEBHOOK_SECRET = os.environ.get('EXTERNAL_WEBHOOK_SECRET', '')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
