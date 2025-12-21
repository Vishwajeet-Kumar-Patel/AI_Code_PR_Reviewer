from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    APP_NAME: str = "AI Code Review System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    MAX_WORKERS: int = 4
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ai_code_review"
    
    # GitHub
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_WEBHOOK_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    
    # JWT & Security
    JWT_SECRET_KEY: str = "CHANGE_THIS_TO_RANDOM_SECRET_KEY_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # OAuth2
    OAUTH_REDIRECT_URI: str = "http://localhost:3000/auth/callback"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 4096
    OPENAI_TEMPERATURE: float = 0.7
    
    # Gemini
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-pro"
    
    # AI Provider
    AI_PROVIDER: str = "openai"  # openai or gemini
    
    # Vector Database
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    VECTOR_DB_COLLECTION: str = "code_best_practices"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    CACHE_TTL: int = 3600
    
    # Review Configuration
    MAX_FILE_SIZE_MB: int = 5
    SUPPORTED_LANGUAGES: List[str] = [
        "python", "javascript", "typescript", "java", "go", 
        "rust", "cpp", "csharp", "ruby", "php"
    ]
    COMPLEXITY_THRESHOLD: int = 10
    SECURITY_SCAN_ENABLED: bool = True
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Paths
    KNOWLEDGE_BASE_PATH: str = "./app/knowledge_base"
    LOGS_PATH: str = "./logs"
    DATA_PATH: str = "./data"
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes"""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    @property
    def is_openai_configured(self) -> bool:
        """Check if OpenAI is configured"""
        return bool(self.OPENAI_API_KEY)
    
    @property
    def is_gemini_configured(self) -> bool:
        """Check if Gemini is configured"""
        return bool(self.GEMINI_API_KEY)
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        if isinstance(self.SUPPORTED_LANGUAGES, str):
            return [lang.strip() for lang in self.SUPPORTED_LANGUAGES.split(",")]
        return self.SUPPORTED_LANGUAGES


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
