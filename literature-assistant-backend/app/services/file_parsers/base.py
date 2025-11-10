"""
文件解析器基类
"""
from abc import ABC, abstractmethod


class FileParser(ABC):
    """文件解析器抽象基类"""
    
    @abstractmethod
    async def parse(self, file_path: str) -> str:
        """
        解析文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件文本内容
        """
        pass
    
    @property
    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """支持的文件扩展名"""
        pass
    
    @property
    @abstractmethod
    def parser_name(self) -> str:
        """解析器名称"""
        pass

