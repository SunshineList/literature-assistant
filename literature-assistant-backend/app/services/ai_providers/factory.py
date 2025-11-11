"""
AI 提供商工厂
"""
from typing import Dict, Type
from app.services.ai_providers.base import AIProvider
from app.services.ai_providers.openai_compatible_provider import OpenAICompatibleProvider
from app.core.exceptions import AIException


class AIProviderFactory:
    """AI 提供商工厂类"""
    
    # 注册的提供商（统一使用OpenAI兼容接口）
    _providers: Dict[str, Type[AIProvider]] = {
        "openai_compatible": OpenAICompatibleProvider,
    }
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[AIProvider]):
        """
        注册新的 AI 提供商
        
        Args:
            name: 提供商名称
            provider_class: 提供商类
        """
        cls._providers[name] = provider_class
    
    @classmethod
    def create_provider(cls, provider_name: str, **config) -> AIProvider:
        """
        创建 AI 提供商实例
        
        Args:
            provider_name: 提供商名称（如 "kimi", "ollama"）
            **config: 配置参数
            
        Returns:
            AI 提供商实例
            
        Raises:
            AIException: 提供商不存在
        """
        provider_class = cls._providers.get(provider_name.lower())
        
        if not provider_class:
            available = ", ".join(cls._providers.keys())
            raise AIException(
                f"不支持的 AI 提供商: {provider_name}。"
                f"可用的提供商: {available}"
            )
        
        return provider_class(**config)
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """获取所有可用的提供商名称"""
        return list(cls._providers.keys())

