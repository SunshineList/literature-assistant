"""
AI 服务 - 使用策略模式和工厂模式
"""
import json
from typing import AsyncGenerator, Optional
from app.core.exceptions import AIException
from app.config import settings
from app.utils.prompt_loader import load_prompt
from app.services.ai_providers.factory import AIProviderFactory
from app.services.ai_providers.base import AIProvider


class AIService:
    """
    AI 服务 - 统一的 AI 服务接口
    
    使用策略模式支持多个 AI 提供商，通过工厂模式创建提供商实例
    """
    
    def __init__(self):
        """初始化 AI 服务"""
        self.provider_name = settings.AI_PROVIDER
        
        # 准备提供商配置
        self.provider_config = {
            "max_tokens": settings.AI_MAX_TOKENS,
            "temperature": settings.AI_TEMPERATURE,
            "timeout": settings.AI_TIMEOUT
        }
        
        # Kimi 特定配置
        if self.provider_name == "kimi":
            self.provider_config.update({
                "base_url": settings.KIMI_BASE_URL,
                "model": settings.KIMI_MODEL
            })
        
        # Ollama 特定配置
        elif self.provider_name == "ollama":
            self.provider_config.update({
                "base_url": settings.OLLAMA_BASE_URL,
                "model": settings.OLLAMA_MODEL
            })
    
    def _get_provider(self, api_key: Optional[str] = None) -> AIProvider:
        """
        获取 AI 提供商实例
        
        Args:
            api_key: API Key（某些提供商需要）
            
        Returns:
            AI 提供商实例
        """
        provider = AIProviderFactory.create_provider(
            self.provider_name,
            **self.provider_config
        )
        
        # 验证 API Key
        if provider.requires_api_key and not api_key:
            raise AIException(f"{provider.name} 需要提供 API Key")
        
        return provider
    
    async def generate_reading_guide_stream(
        self,
        content: str,
        api_key: Optional[str] = None
    ) -> AsyncGenerator[dict, None]:
        """
        流式生成阅读指南
        
        Args:
            content: 文献内容
            api_key: API Key（某些提供商需要）
            
        Yields:
            SSE消息字典
        """
        # 加载系统提示词
        system_prompt = load_prompt("literature-guide-system-prompt")
        
        # 限制内容长度
        max_content_length = 30000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "...(内容过长已截断)"
        
        # 构建用户消息
        user_message = f"""请为以下文献生成阅读指南：

{content}"""
        
        try:
            # 获取提供商
            provider = self._get_provider(api_key)
            
            # 流式生成
            async for message in provider.generate_stream(
                system_prompt=system_prompt,
                user_message=user_message,
                api_key=api_key
            ):
                yield message
        
        except AIException:
            raise
        except Exception as e:
            raise AIException(f"AI 服务异常: {str(e)}")
    
    async def extract_tags_and_description(
        self,
        reading_guide: str,
        api_key: Optional[str] = None
    ) -> tuple[list[str], str]:
        """
        从阅读指南中提取标签和描述
        
        Args:
            reading_guide: 已生成的阅读指南
            api_key: API Key（某些提供商需要）
            
        Returns:
            (标签列表, 描述)
        """
        # 加载分类提示词
        system_prompt = load_prompt("literature-classification-system-prompt")
        
        # 限制内容长度
        max_content_length = 5000
        if len(reading_guide) > max_content_length:
            reading_guide = reading_guide[:max_content_length]
        
        user_message = f"""文献阅读指南：

{reading_guide}"""
        
        try:
            # 获取提供商
            provider = self._get_provider(api_key)
            
            # 非流式生成
            content = await provider.generate(
                system_prompt=system_prompt,
                user_message=user_message,
                api_key=api_key,
                temperature=0.3  # 降低随机性
            )
            
            # 解析结果
            return self._parse_classification_result(content)
        
        except Exception as e:
            print(f"提取标签和描述失败: {str(e)}")
            return [], "AI 自动生成的文献描述"
    
    def _parse_classification_result(self, content: str) -> tuple[list[str], str]:
        """
        解析分类结果
        
        Args:
            content: AI 返回的内容
            
        Returns:
            (标签列表, 描述)
        """
        try:
            # 尝试提取 JSON
            # 有些模型会返回 ```json ... ```，需要清理
            content = content.strip()
            
            # 移除可能的 markdown 代码块标记
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            # 解析 JSON
            result = json.loads(content)
            tags = result.get("tags", [])[:5]  # 最多5个标签
            description = result.get("desc", result.get("description", ""))[:200]  # 最多200字
            
            return tags, description
        
        except json.JSONDecodeError:
            # 如果不是有效的 JSON，返回默认值
            print(f"JSON 解析失败，返回默认值")
            return [], content[:200] if content else "AI 自动生成的文献描述"
    
    def get_provider_info(self) -> dict:
        """
        获取当前提供商信息
        
        Returns:
            提供商信息字典
        """
        try:
            provider = self._get_provider()
            return {
                "name": provider.name,
                "requires_api_key": provider.requires_api_key,
                "config": self.provider_config
            }
        except Exception as e:
            return {
                "name": self.provider_name,
                "error": str(e)
            }


# 创建全局实例
ai_service = AIService()
