"""
TXT 文件解析器
"""
import aiofiles
from app.services.file_parsers.base import FileParser


class TxtParser(FileParser):
    """TXT 文件解析器"""
    
    async def parse(self, file_path: str) -> str:
        """
        解析 TXT 文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容
        """
        try:
            # 尝试多种编码读取文件
            encodings = ['utf-8', 'gbk', 'gb2312', 'big5', 'latin-1']
            
            for encoding in encodings:
                try:
                    async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
                        content = await f.read()
                        
                    # 如果成功读取且内容不为空，返回
                    if content and content.strip():
                        return content.strip()
                        
                except (UnicodeDecodeError, LookupError):
                    # 如果当前编码失败，尝试下一个
                    continue
            
            # 如果所有编码都失败，返回错误信息
            raise ValueError(f"无法使用支持的编码读取文件: {file_path}")
            
        except Exception as e:
            raise Exception(f"TXT 文件解析失败: {str(e)}")

    @property
    def supported_extensions(self) -> list[str]:
        """支持的文件扩展名"""
        return ['txt']
    
    @property
    def parser_name(self) -> str:
        """解析器名称"""
        return 'Txt Parser'