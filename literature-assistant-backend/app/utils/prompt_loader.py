"""
提示词加载工具
"""
import os
from functools import lru_cache
from typing import Optional
from pathlib import Path


class PromptLoader:
    """提示词加载器"""
    
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

