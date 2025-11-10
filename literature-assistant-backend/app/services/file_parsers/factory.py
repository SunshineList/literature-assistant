"""
文件解析器工厂
"""
from typing import Dict, Type
from app.services.file_parsers.base import FileParser
from app.services.file_parsers.pdf_parser import PDFParser
from app.services.file_parsers.word_parser import WordParser
from app.services.file_parsers.markdown_parser import MarkdownParser
from app.core.exceptions import FileException


class FileParserFactory:
    """文件解析器工厂"""
    
    # 注册的解析器
    _parsers: Dict[str, Type[FileParser]] = {}
    
    # 扩展名到解析器的映射
    _extension_map: Dict[str, Type[FileParser]] = {}
    
    @classmethod
    def _init_parsers(cls):
        """初始化默认解析器"""
        if not cls._parsers:
            cls.register_parser(PDFParser)
            cls.register_parser(WordParser)
            cls.register_parser(MarkdownParser)
    
    @classmethod
    def register_parser(cls, parser_class: Type[FileParser]):
        """
        注册文件解析器
        
        Args:
            parser_class: 解析器类
        """
        parser_instance = parser_class()
        parser_name = parser_instance.parser_name
        
        # 注册解析器
        cls._parsers[parser_name] = parser_class
        
        # 建立扩展名映射
        for ext in parser_instance.supported_extensions:
            cls._extension_map[ext.lower()] = parser_class
    
    @classmethod
    def get_parser(cls, file_extension: str) -> FileParser:
        """
        根据文件扩展名获取解析器
        
        Args:
            file_extension: 文件扩展名（如 'pdf', 'docx'）
            
        Returns:
            文件解析器实例
            
        Raises:
            FileException: 不支持的文件类型
        """
        cls._init_parsers()
        
        ext = file_extension.lower().lstrip('.')
        parser_class = cls._extension_map.get(ext)
        
        if not parser_class:
            supported = ", ".join(cls._extension_map.keys())
            raise FileException(
                f"不支持的文件类型: {file_extension}。"
                f"支持的类型: {supported}"
            )
        
        return parser_class()
    
    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """获取所有支持的文件扩展名"""
        cls._init_parsers()
        return list(cls._extension_map.keys())
    
    @classmethod
    def is_supported(cls, file_extension: str) -> bool:
        """检查文件类型是否支持"""
        cls._init_parsers()
        ext = file_extension.lower().lstrip('.')
        return ext in cls._extension_map

