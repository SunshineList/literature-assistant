"""
统一响应格式模块
"""
from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')


class Response(BaseModel, Generic[T]):
    """统一响应格式"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[T] = None
    code: int = 200

    @classmethod
    def ok(cls, data: Any = None, message: str = "操作成功") -> "Response":
        """成功响应"""
        return cls(success=True, message=message, data=data, code=200)

    @classmethod
    def error(cls, message: str = "操作失败", code: int = 500) -> "Response":
        """错误响应"""
        return cls(success=False, message=message, data=None, code=code)


class PageData(BaseModel, Generic[T]):
    """分页数据"""
    records: list[T] = []
    total: int = 0
    pageNum: int = 1
    pageSize: int = 10

