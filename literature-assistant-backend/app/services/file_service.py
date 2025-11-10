"""
文件处理服务 - 使用策略模式和工厂模式
"""
import os
import aiofiles
from typing import Tuple
from fastapi import UploadFile
from app.core.exceptions import FileException
from app.utils.file_utils import generate_file_path, get_file_extension, is_allowed_file
from app.config import settings
from app.services.file_parsers.factory import FileParserFactory


class FileService:
    """
    文件处理服务
    
    使用策略模式处理不同类型的文件解析
    """
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.max_file_size = settings.MAX_FILE_SIZE
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS
        
        # 确保上传目录存在
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def save_file(self, file: UploadFile) -> Tuple[str, str, int, str]:
        """
        保存上传的文件
        
        Args:
            file: 上传的文件
            
        Returns:
            (完整路径, 相对路径, 文件大小, 文件类型)
        """
        # 验证文件
        await self._validate_file(file)
        
        # 生成文件路径
        full_path, relative_path = generate_file_path(file.filename, self.upload_dir)
        
        # 保存文件
        file_size = 0
        async with aiofiles.open(full_path, 'wb') as f:
            while chunk := await file.read(8192):  # 8KB chunks
                file_size += len(chunk)
                await f.write(chunk)
        
        # 获取文件类型
        file_type = get_file_extension(file.filename)
        
        return full_path, relative_path, file_size, file_type
    
    async def _validate_file(self, file: UploadFile):
        """验证文件"""
        if not file or not file.filename:
            raise FileException("请选择文件")
        
        # 检查文件类型
        if not is_allowed_file(file.filename, self.allowed_extensions):
            raise FileException(f"不支持的文件类型，仅支持: {', '.join(self.allowed_extensions)}")
        
        # 检查文件大小
        file.file.seek(0, 2)  # 移动到文件末尾
        file_size = file.file.tell()
        file.file.seek(0)  # 重置到开始
        
        if file_size > self.max_file_size:
            raise FileException(f"文件大小超过限制({self.max_file_size / 1024 / 1024}MB)")
        
        if file_size == 0:
            raise FileException("文件内容为空")
    
    async def extract_content(self, file_path: str, file_type: str) -> str:
        """
        提取文件内容 - 使用策略模式
        
        Args:
            file_path: 文件路径
            file_type: 文件类型
            
        Returns:
            文件文本内容
        """
        try:
            # 通过工厂获取对应的解析器
            parser = FileParserFactory.get_parser(file_type)
            
            # 使用解析器提取内容
            content = await parser.parse(file_path)
            
            return content
        except FileException:
            raise
        except Exception as e:
            raise FileException(f"文件内容提取失败: {str(e)}")
    
    def delete_file(self, file_path: str):
        """删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"删除文件失败: {str(e)}")
    
    def get_supported_extensions(self) -> list[str]:
        """获取支持的文件扩展名"""
        return FileParserFactory.get_supported_extensions()


# 创建全局实例
file_service = FileService()
