"""
Markdown 文件解析器
"""
import aiofiles
from app.services.file_parsers.base import FileParser
from app.core.exceptions import FileException


class MarkdownParser(FileParser):
    """Markdown 文件解析器"""
    
    async def parse(self, file_path: str) -> str:
        """解析Markdown内容"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            if not content.strip():
                raise FileException("Markdown文件内容为空")
            
            return content
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                async with aiofiles.open(file_path, 'r', encoding='gbk') as f:
                    content = await f.read()
                return content
            except:
                raise FileException("Markdown文件编码错误")
        except Exception as e:
            raise FileException(f"Markdown文件读取失败: {str(e)}")
    
    @property
    def supported_extensions(self) -> list[str]:
        return ['md', 'markdown']
    
    @property
    def parser_name(self) -> str:
        return "Markdown Parser"

