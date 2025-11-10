"""
文件处理工具
"""
import os
import hashlib
from datetime import datetime
from typing import Tuple


def generate_file_path(original_filename: str, upload_dir: str) -> Tuple[str, str]:
    """
    生成文件存储路径
    
    Args:
        original_filename: 原始文件名
        upload_dir: 上传目录
        
    Returns:
        (完整路径, 相对路径)
    """
    # 获取文件扩展名
    _, ext = os.path.splitext(original_filename)
    
    # 使用时间戳和哈希生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    hash_str = hashlib.md5(f"{original_filename}{timestamp}".encode()).hexdigest()[:8]
    filename = f"{timestamp}_{hash_str}{ext}"
    
    # 按日期分目录存储
    date_dir = datetime.now().strftime("%Y%m%d")
    relative_path = os.path.join(date_dir, filename)
    full_path = os.path.join(upload_dir, relative_path)
    
    # 确保目录存在
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    return full_path, relative_path


def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名（不包含点）
    
    Args:
        filename: 文件名
        
    Returns:
        扩展名
    """
    _, ext = os.path.splitext(filename)
    return ext.lstrip('.').lower()


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 字节数
        
    Returns:
        格式化后的文件大小字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def is_allowed_file(filename: str, allowed_extensions: list) -> bool:
    """
    检查文件类型是否允许
    
    Args:
        filename: 文件名
        allowed_extensions: 允许的扩展名列表
        
    Returns:
        是否允许
    """
    ext = get_file_extension(filename)
    return ext in [e.lower() for e in allowed_extensions]

