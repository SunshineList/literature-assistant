"""
Kimi AI 提供商实现
"""
from typing import AsyncGenerator
from openai import AsyncOpenAI
from app.services.ai_providers.base import AIProvider
from app.core.exceptions import AIException


class KimiProvider(AIProvider):
    """Kimi AI 提供商（基于 OpenAI SDK）"""
    
    def __init__(self, **config):
        super().__init__(**config)
        self.base_url = config.get("base_url", "https://api.moonshot.cn/v1")
        self.model = config.get("model", "moonshot-v1-8k")
        self.max_tokens = config.get("max_tokens", 20480)
        self.temperature = config.get("temperature", 0.7)
        self.timeout = config.get("timeout", 300)
    
    def _get_client(self, api_key: str) -> AsyncOpenAI:
        """获取 OpenAI 客户端"""
        if not api_key:
            raise AIException("Kimi AI 需要提供 API Key")
        
        return AsyncOpenAI(
            api_key=api_key,
            base_url=self.base_url,
            timeout=self.timeout
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
                    
                    # 提取内容
                    if delta.content:
                        yield {"type": "content", "data": delta.content}
                    
                    # 检查是否完成
                    if chunk.choices[0].finish_reason == "stop":
                        break
            
            # 发送完成事件
            yield {"type": "complete", "data": "生成完成"}
        
        except Exception as e:
            raise AIException(f"Kimi AI 调用失败: {str(e)}")
    
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
                stream=False,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature)
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            raise AIException(f"Kimi AI 调用失败: {str(e)}")
    
    @property
    def name(self) -> str:
        return "Kimi AI"
    
    @property
    def requires_api_key(self) -> bool:
        return True

