"""
AI 服务 - 使用策略模式和工厂模式
"""
import json
from typing import AsyncGenerator, List, Dict
from app.core.exceptions import AIException
from app.utils.prompt_loader import load_prompt, prompt_loader
from app.services.ai_providers.factory import AIProviderFactory
from app.models.ai_models import AIModel


class AIService:
    """
    AI 服务 - 统一的 AI 服务接口
    
    使用策略模式支持多个 AI 提供商，通过工厂模式创建提供商实例
    """
    
    async def generate_reading_guide_stream(
        self,
        content: str,
        ai_model: AIModel,
        expert_id: str = "academic-mentor"
    ) -> AsyncGenerator[dict, None]:
        """
        流式生成阅读指南（使用指定专家）
        
        Args:
            content: 文献内容
            ai_model: AI模型配置
            expert_id: 专家ID，默认为"academic-mentor"（学术导师）
            
        Yields:
            SSE消息字典
        """
        try:
            # 加载专家提示词
            system_prompt = prompt_loader.load_expert_prompt(expert_id)
        except FileNotFoundError as e:
            raise AIException(f"专家不存在: {str(e)}")
        
        # 限制内容长度
        max_content_length = 30000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "...(内容过长已截断)"
        
        # 构建用户消息
        user_message = f"""请为以下文献生成阅读指南：

{content}"""
        
        try:
            # 使用用户配置的AI模型
            config = {
                "base_url": ai_model.base_url,
                "model": ai_model.model_name,
                "max_tokens": ai_model.max_tokens,
                "temperature": float(ai_model.temperature),
                "timeout": 300  # 默认超时时间 5 分钟
            }
            
            # 创建提供商实例（统一使用openai_compatible）
            ai_provider = AIProviderFactory.create_provider("openai_compatible", **config)
            
            # 流式生成
            async for message in ai_provider.generate_stream(
                system_prompt=system_prompt,
                user_message=user_message,
                api_key=ai_model.api_key
            ):
                yield message
        
        except AIException:
            raise
        except Exception as e:
            raise AIException(f"AI 服务异常: {str(e)}")
    
    async def extract_tags_and_description(
        self,
        reading_guide: str,
        ai_model: AIModel
    ) -> tuple[list[str], str]:
        """
        从阅读指南中提取标签和描述
        
        Args:
            reading_guide: 已生成的阅读指南
            ai_model: AI模型配置
            
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
            # 使用用户配置的AI模型
            config = {
                "base_url": ai_model.base_url,
                "model": ai_model.model_name,
                "max_tokens": ai_model.max_tokens,
                "temperature": 0.3,  # 降低随机性
                "timeout": 300  # 默认超时时间 5 分钟
            }
            
            # 创建提供商实例
            provider = AIProviderFactory.create_provider("openai_compatible", **config)
            
            # 非流式生成
            content = await provider.generate(
                system_prompt=system_prompt,
                user_message=user_message,
                api_key=ai_model.api_key
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
    
    def get_available_experts(self) -> List[Dict[str, str]]:
        """
        获取所有可用的专家列表
        
        Returns:
            专家列表
        """
        return prompt_loader.get_available_experts()
    


# 创建全局实例
ai_service = AIService()
