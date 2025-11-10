"""
日期处理工具
"""
from datetime import datetime
from typing import Optional


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """
    解析日期字符串
    
    Args:
        date_str: 日期字符串
        
    Returns:
        datetime对象或None
    """
    if not date_str:
        return None
    
    # 尝试多种日期格式
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d",
        "%Y/%m/%d %H:%M:%S",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    return None


def format_datetime(dt: Optional[datetime], fmt: str = "%Y-%m-%d %H:%M:%S") -> Optional[str]:
    """
    格式化日期时间
    
    Args:
        dt: datetime对象
        fmt: 格式字符串
        
    Returns:
        格式化后的字符串或None
    """
    if not dt:
        return None
    return dt.strftime(fmt)

