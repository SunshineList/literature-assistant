"""
AI 提供商模块
"""
from app.services.ai_providers.base import AIProvider
from app.services.ai_providers.kimi_provider import KimiProvider
from app.services.ai_providers.ollama_provider import OllamaProvider

__all__ = ["AIProvider", "KimiProvider", "OllamaProvider"]

