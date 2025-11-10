"""
Ollama 提供商实现
"""
from typing import AsyncGenerator
import ollama
from app.services.ai_providers.base import AIProvider
from app.core.exceptions import AIException


class OllamaProvider(AIProvider):
    """Ollama 提供商"""
    
    def __init__(self, **config):
        super().__init__(**config)
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.model = config.get("model", "qwen2.5:latest")
        self.max_tokens = config.get("max_tokens", 20480)
        self.temperature = config.get("temperature", 0.7)
    
    def _get_client(self) -> ollama.AsyncClient:
        """获取 Ollama 客户端"""
        return ollama.AsyncClient(host=self.base_url)
    
    async def generate_stream(
        self,
        system_prompt: str,
        user_message: str,
        api_key: str = None,
        **kwargs
    ) -> AsyncGenerator[dict, None]:
        """流式生成内容"""
        try:
            client = self._get_client()
            
            # 发送开始事件
            yield {"type": "start", "data": "开始生成内容..."}
            
            # 调用流式 API
            stream = await client.chat(
                model=kwargs.get("model", self.model),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                stream=True,
                options={
                    "temperature": kwargs.get("temperature", self.temperature),
                    "num_predict": kwargs.get("max_tokens", self.max_tokens)
                }
            )
            
            # 流式读取响应
            async for chunk in stream:
                if "message" in chunk and "content" in chunk["message"]:
                    content = chunk["message"]["content"]
                    if content:
                        yield {"type": "content", "data": content}
                
                # 检查是否完成
                if chunk.get("done", False):
                    break
            
            # 发送完成事件
            yield {"type": "complete", "data": "生成完成"}
        
        except Exception as e:
            raise AIException(f"Ollama 调用失败: {str(e)}")
    
    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        api_key: str = None,
        **kwargs
    ) -> str:
        """非流式生成内容"""
        try:
            client = self._get_client()
            
            response = await client.chat(
                model=kwargs.get("model", self.model),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                stream=False,
                options={
                    "temperature": kwargs.get("temperature", self.temperature),
                    "num_predict": kwargs.get("max_tokens", self.max_tokens)
                }
            )
            
            return response["message"]["content"]
        
        except Exception as e:
            raise AIException(f"Ollama 调用失败: {str(e)}")
    
    @property
    def name(self) -> str:
        return "Ollama"
    
    @property
    def requires_api_key(self) -> bool:
        return False

