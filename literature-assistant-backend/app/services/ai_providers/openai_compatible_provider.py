"""
OpenAI兼容提供商实现
支持所有遵循OpenAI API规范的模型，包括：
- 通义千问 (Qwen)
- DeepSeek
- Moonshot (Kimi)
- 本地Ollama (通过OpenAI兼容接口)
等
"""
from typing import AsyncGenerator
from openai import AsyncOpenAI
from app.services.ai_providers.base import AIProvider
from app.core.exceptions import AIException


class OpenAICompatibleProvider(AIProvider):
    """OpenAI兼容提供商"""
    
    def __init__(self, **config):
        super().__init__(**config)
        self.base_url = config.get("base_url")
        self.model = config.get("model")
        self.max_tokens = config.get("max_tokens", 4096)
        self.temperature = float(config.get("temperature", 0.7))
    
    def _get_client(self, api_key: str = None) -> AsyncOpenAI:
        """获取OpenAI兼容客户端"""
        return AsyncOpenAI(
            api_key=api_key or "dummy",  # 某些服务不需要key
            base_url=self.base_url
        )
    
    async def generate_stream(
        self,
        system_prompt: str,
        user_message: str,
        api_key: str = None,
        **kwargs
    ) -> AsyncGenerator[dict, None]:
        """流式生成内容"""
        try:
            client = self._get_client(api_key)
            
            # 发送开始事件
            yield {"type": "start", "data": "开始生成内容..."}
            
            # 调用流式 API
            stream = await client.chat.completions.create(
                model=kwargs.get("model", self.model),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                stream=True,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature)
            )
            
            # 流式读取响应
            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield {"type": "content", "data": delta.content}
            
            # 发送完成事件
            yield {"type": "complete", "data": "生成完成"}
        
        except Exception as e:
            raise AIException(f"OpenAI兼容API调用失败: {str(e)}")
    
    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        api_key: str = None,
        **kwargs
    ) -> str:
        """非流式生成内容"""
        try:
            client = self._get_client(api_key)
            
            response = await client.chat.completions.create(
                model=kwargs.get("model", self.model),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature)
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            raise AIException(f"OpenAI兼容API调用失败: {str(e)}")
    
    @property
    def name(self) -> str:
        return "OpenAI Compatible"
    
    @property
    def requires_api_key(self) -> bool:
        # 大多数服务需要API Key，但本地Ollama不需要
        return True

