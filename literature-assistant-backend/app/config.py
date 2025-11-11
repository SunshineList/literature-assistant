"""
应用配置模块
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    APP_NAME: str = "Literature Assistant API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # JWT 配置
    SECRET_KEY: str = ""
    
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8086
    API_PREFIX: str = "/api"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/literature_assistant.db"
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads/documents"
    MAX_FILE_SIZE: int = 52428800  # 50MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "doc", "docx", "md", "markdown", "txt"]
    
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
