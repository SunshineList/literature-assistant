"""
应用配置模块
"""
from pydantic_settings import BaseSettings
from typing import List, Literal


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    APP_NAME: str = "Literature Assistant API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8086
    API_PREFIX: str = "/api"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/literature_assistant.db"
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads/documents"
    MAX_FILE_SIZE: int = 52428800  # 50MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "doc", "docx", "md", "markdown"]
    
    # AI 服务配置
    AI_PROVIDER: Literal["kimi", "ollama"] = "kimi"  # AI 服务提供商：kimi 或 ollama
    
    # Kimi AI 配置
    KIMI_BASE_URL: str = "https://api.moonshot.cn/v1"
    KIMI_MODEL: str = "moonshot-v1-8k"
    
    # Ollama 配置
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:latest"
    
    # 通用 AI 配置
    AI_MAX_TOKENS: int = 20480
    AI_TEMPERATURE: float = 0.7
    AI_TIMEOUT: int = 300  # 秒
    
    # CORS 配置
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
