"""
提示词加载工具
"""
import os
from functools import lru_cache
from typing import Optional, List, Dict
from pathlib import Path


class PromptLoader:
    """提示词加载器"""
    
    # 专家配置：定义所有可用的专家类型
    EXPERTS = {
        "academic-mentor": {
            "id": "academic-mentor",
            "name": "学术导师",
            "description": "资深学术导师，擅长生成详细的学术文献阅读指南，包含结构化解析、关键术语、思维导图等",
            "icon": "🎓",
            "category": "学术",
            "prompt_file": "experts/literature-guide-system-prompt.txt"  # 使用原有的提示词文件
        },
        "general-summary": {
            "id": "general-summary",
            "name": "通用总结专家",
            "description": "适用于各类文章的快速总结，提供结构化的核心要点",
            "icon": "📝",
            "category": "通用",
            "prompt_file": "experts/general-summary.txt"
        },
        "government-document-analyst": {
            "id": "government-document-analyst",
            "name": "申论与政府文件分析专家",
            "description": "专注于政府文件、政策文本和申论材料的深度解读",
            "icon": "🏛️",
            "category": "政务",
            "prompt_file": "experts/government-document-analyst.txt"
        },
        "business-analyst": {
            "id": "business-analyst",
            "name": "商业分析专家",
            "description": "解读商业报告、市场分析和企业战略文档",
            "icon": "💼",
            "category": "商业",
            "prompt_file": "experts/business-analyst.txt"
        },
        "legal-analyst": {
            "id": "legal-analyst",
            "name": "法律文件分析专家",
            "description": "分析法律文件、合同条款和法律案例",
            "icon": "⚖️",
            "category": "法律",
            "prompt_file": "experts/legal-analyst.txt"
        },
        "technology-analyst": {
            "id": "technology-analyst",
            "name": "技术文档分析专家",
            "description": "解读技术文档、架构设计和技术方案",
            "icon": "💻",
            "category": "技术",
            "prompt_file": "experts/technology-analyst.txt"
        }
    }
    
    def __init__(self, prompts_dir: Optional[str] = None):
        """
        初始化提示词加载器
        
        Args:
            prompts_dir: 提示词文件目录，默认为 app/prompts
        """
        if prompts_dir is None:
            # 获取当前文件所在目录的上级目录下的 prompts 文件夹
            current_dir = Path(__file__).parent.parent
            prompts_dir = current_dir / "prompts"
        
        self.prompts_dir = Path(prompts_dir)
        self.experts_dir = self.prompts_dir / "experts"
        
        if not self.prompts_dir.exists():
            raise FileNotFoundError(f"提示词目录不存在: {self.prompts_dir}")
    
    @lru_cache(maxsize=32)
    def load_prompt(self, prompt_name: str) -> str:
        """
        加载提示词文件（带缓存）
        
        Args:
            prompt_name: 提示词文件名（不含扩展名）或完整文件名
            
        Returns:
            提示词内容
            
        Raises:
            FileNotFoundError: 文件不存在
        """
        # 如果没有扩展名，默认添加 .txt
        if not prompt_name.endswith('.txt'):
            prompt_name = f"{prompt_name}.txt"
        
        prompt_path = self.prompts_dir / prompt_name
        
        if not prompt_path.exists():
            raise FileNotFoundError(f"提示词文件不存在: {prompt_path}")
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content.strip()
        except UnicodeDecodeError:
            # 尝试其他编码
            with open(prompt_path, 'r', encoding='gbk') as f:
                content = f.read()
            return content.strip()
    
    def get_prompt(self, prompt_name: str, **kwargs) -> str:
        """
        获取提示词并支持变量替换
        
        Args:
            prompt_name: 提示词文件名
            **kwargs: 要替换的变量（使用 {variable_name} 格式）
            
        Returns:
            处理后的提示词
        """
        prompt = self.load_prompt(prompt_name)
        
        # 如果有变量，进行替换
        if kwargs:
            prompt = prompt.format(**kwargs)
        
        return prompt
    
    def reload_prompt(self, prompt_name: str) -> str:
        """
        重新加载提示词（清除缓存）
        
        Args:
            prompt_name: 提示词文件名
            
        Returns:
            提示词内容
        """
        # 清除缓存
        self.load_prompt.cache_clear()
        return self.load_prompt(prompt_name)
    
    def get_available_experts(self) -> List[Dict[str, str]]:
        """
        获取所有可用的专家列表
        
        Returns:
            专家列表，每个专家包含 id, name, description, icon, category
        """
        available_experts = []
        
        for expert_id, expert_info in self.EXPERTS.items():
            # 检查对应的提示词文件是否存在
            prompt_file = expert_info.get('prompt_file', f"experts/{expert_id}.txt")
            expert_file = self.prompts_dir / prompt_file
            if expert_file.exists():
                # 返回时不包含prompt_file字段
                expert_data = {k: v for k, v in expert_info.items() if k != 'prompt_file'}
                available_experts.append(expert_data)
        
        return available_experts
    
    def load_expert_prompt(self, expert_id: str) -> str:
        """
        加载专家提示词
        
        Args:
            expert_id: 专家ID
            
        Returns:
            专家提示词内容
            
        Raises:
            FileNotFoundError: 专家不存在或提示词文件不存在
        """
        if expert_id not in self.EXPERTS:
            raise FileNotFoundError(f"专家不存在: {expert_id}")
        
        # 获取专家配置中的prompt_file，如果没有则使用默认路径
        expert_info = self.EXPERTS[expert_id]
        prompt_file = expert_info.get('prompt_file', f"experts/{expert_id}.txt")
        
        return self.load_prompt(prompt_file)
    
    def get_expert_info(self, expert_id: str) -> Optional[Dict[str, str]]:
        """
        获取专家信息
        
        Args:
            expert_id: 专家ID
            
        Returns:
            专家信息字典，如果不存在则返回 None
        """
        return self.EXPERTS.get(expert_id)


# 创建全局实例
prompt_loader = PromptLoader()


# 便捷函数
def load_prompt(prompt_name: str, **kwargs) -> str:
    """
    加载提示词的便捷函数
    
    Args:
        prompt_name: 提示词文件名
        **kwargs: 要替换的变量
        
    Returns:
        提示词内容
    """
    return prompt_loader.get_prompt(prompt_name, **kwargs)


# 装饰器：为函数注入提示词
def with_prompt(prompt_name: str, param_name: str = "system_prompt"):
    """
    装饰器：为函数自动注入提示词
    
    Args:
        prompt_name: 提示词文件名
        param_name: 注入的参数名，默认为 "system_prompt"
        
    Example:
        @with_prompt("literature-guide-system-prompt")
        def generate_guide(content: str, system_prompt: str = None):
            # system_prompt 会被自动注入
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 如果参数中没有提供 prompt，则自动加载
            if param_name not in kwargs or kwargs[param_name] is None:
                kwargs[param_name] = prompt_loader.load_prompt(prompt_name)
            return func(*args, **kwargs)
        return wrapper
    return decorator

