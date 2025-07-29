"""Configuration settings for the application."""

import os
from typing import Optional


class Settings:
    """Application settings."""
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Session Configuration
    SESSION_TTL: int = int(os.getenv("SESSION_TTL", "86400"))  # 24 hours default
    
    # TTS Configuration
    AUDIO_TTL: int = int(os.getenv("AUDIO_TTL", "7200"))  # 2 hours default
    TTS_MODEL: str = os.getenv("TTS_MODEL", "tts-1")
    
    # LLM Configuration
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "200"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.8"))
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Pipecat Configuration
    PIPECAT_LOG_LEVEL: str = os.getenv("PIPECAT_LOG_LEVEL", "INFO")
    TTS_PROVIDER: str = os.getenv("TTS_PROVIDER", "openai")  # openai, elevenlabs
    ELEVENLABS_API_KEY: Optional[str] = os.getenv("ELEVENLABS_API_KEY")


settings = Settings()
