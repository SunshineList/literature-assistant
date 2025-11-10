"""
Word 文件解析器
"""
from app.services.file_parsers.base import FileParser
from app.core.exceptions import FileException


class WordParser(FileParser):
    """Word 文件解析器"""
    
    async def parse(self, file_path: str) -> str:
        """解析Word文档内容"""
        try:
            from docx import Document
            
            doc = Document(file_path)
            text_parts = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            content = '\n\n'.join(text_parts)
            if not content.strip():
                raise FileException("Word文档无文本内容")
            
            return content
        except ImportError:
            raise FileException("Word处理模块未安装，请安装 python-docx")
        except Exception as e:
            raise FileException(f"Word文档解析失败: {str(e)}")
    
    @property
    def supported_extensions(self) -> list[str]:
        return ['doc', 'docx']
    
    @property
    def parser_name(self) -> str:
        return "Word Parser"

