"""
PDF 文件解析器
"""
from app.services.file_parsers.base import FileParser
from app.core.exceptions import FileException


class PDFParser(FileParser):
    """PDF 文件解析器"""
    
    async def parse(self, file_path: str) -> str:
        """解析PDF内容"""
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(file_path)
            text_parts = []
            
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            content = '\n\n'.join(text_parts)
            if not content.strip():
                raise FileException("PDF文件无法提取文本内容")
            
            return content
        except ImportError:
            raise FileException("PDF处理模块未安装，请安装 PyPDF2")
        except Exception as e:
            raise FileException(f"PDF文件解析失败: {str(e)}")
    
    @property
    def supported_extensions(self) -> list[str]:
        return ['pdf']
    
    @property
    def parser_name(self) -> str:
        return "PDF Parser"

