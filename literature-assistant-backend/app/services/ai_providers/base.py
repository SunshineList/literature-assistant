"""
AI 提供商基类 - 定义统一接口
"""
from abc import ABC, abstractmethod
from typing import AsyncGenerator


class AIProvider(ABC):
    """AI 提供商抽象基类"""
    
    def __init__(self, **config):
        """
        初始化提供商
        
        Args:
            **config: 配置参数
        """
        self.config = config
    
    @abstractmethod
    async def generate_stream(
        self,
        system_prompt: str,
        user_message: str,
        api_key: str = None,
        **kwargs
    ) -> AsyncGenerator[dict, None]:
        """
        流式生成内容
        
        Args:
            system_prompt: 系统提示词
            user_message: 用户消息
            api_key: API Key（可选）
            **kwargs: 其他参数
            
        Yields:
            {"type": "content", "data": "..."}
            {"type": "start", "data": "..."}
            {"type": "complete", "data": "..."}
        """
        pass
    
    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        api_key: str = None,
        **kwargs
    ) -> str:
        """
        非流式生成内容
        
        Args:
            system_prompt: 系统提示词
            user_message: 用户消息
            api_key: API Key（可选）
            **kwargs: 其他参数
            
        Returns:
            生成的内容
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """提供商名称"""
        pass
    
    @property
    @abstractmethod
    def requires_api_key(self) -> bool:
        """是否需要 API Key"""
        pass

