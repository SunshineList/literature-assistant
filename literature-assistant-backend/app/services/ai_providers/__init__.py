"""
AI 提供商模块
"""
from app.services.ai_providers.base import AIProvider
from app.services.ai_providers.openai_compatible_provider import OpenAICompatibleProvider

__all__ = ["OpenAICompatibleProvider"]

