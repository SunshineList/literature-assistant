"""
响应构建器 - 使用建造者模式
"""
from typing import Any, Optional, TypeVar, Generic
from app.core.response import Response, PageData

T = TypeVar('T')


class ResponseBuilder(Generic[T]):
    """
    响应构建器
    
    使用建造者模式构建统一的 API 响应
    """
    
    def __init__(self):
        """初始化构建器"""
        self._success: bool = True
        self._message: str = "操作成功"
        self._data: Optional[T] = None
        self._code: int = 200
    
    def success(self, is_success: bool = True) -> "ResponseBuilder[T]":
        """
        设置成功状态
        
        Args:
            is_success: 是否成功
            
        Returns:
            self (支持链式调用)
        """
        self._success = is_success
        return self
    
    def message(self, message: str) -> "ResponseBuilder[T]":
        """
        设置消息
        
        Args:
            message: 消息内容
            
        Returns:
            self (支持链式调用)
        """
        self._message = message
        return self
    
    def data(self, data: T) -> "ResponseBuilder[T]":
        """
        设置数据
        
        Args:
            data: 响应数据
            
        Returns:
            self (支持链式调用)
        """
        self._data = data
        return self
    
    def code(self, code: int) -> "ResponseBuilder[T]":
        """
        设置状态码
        
        Args:
            code: HTTP 状态码
            
        Returns:
            self (支持链式调用)
        """
        self._code = code
        return self
    
    def build(self) -> Response[T]:
        """
        构建响应对象
        
        Returns:
            Response 对象
        """
        return Response(
            success=self._success,
            message=self._message,
            data=self._data,
            code=self._code
        )
    
    @classmethod
    def ok(cls, data: T = None, message: str = "操作成功") -> Response[T]:
        """
        快速创建成功响应
        
        Args:
            data: 响应数据
            message: 消息
            
        Returns:
            Response 对象
        """
        return cls().success(True).message(message).data(data).code(200).build()
    
    @classmethod
    def error(cls, message: str = "操作失败", code: int = 500) -> Response:
        """
        快速创建错误响应
        
        Args:
            message: 错误消息
            code: 错误代码
            
        Returns:
            Response 对象
        """
        return cls().success(False).message(message).data(None).code(code).build()
    
    @classmethod
    def not_found(cls, message: str = "资源未找到") -> Response:
        """快速创建404响应"""
        return cls().error(message, 404)
    
    @classmethod
    def unauthorized(cls, message: str = "未授权") -> Response:
        """快速创建401响应"""
        return cls().error(message, 401)
    
    @classmethod
    def forbidden(cls, message: str = "禁止访问") -> Response:
        """快速创建403响应"""
        return cls().error(message, 403)
    
    @classmethod
    def bad_request(cls, message: str = "请求参数错误") -> Response:
        """快速创建400响应"""
        return cls().error(message, 400)


class PageDataBuilder(Generic[T]):
    """
    分页数据构建器
    
    使用建造者模式构建分页响应
    """
    
    def __init__(self):
        """初始化构建器"""
        self._records: list[T] = []
        self._total: int = 0
        self._page_num: int = 1
        self._page_size: int = 10
    
    def records(self, records: list[T]) -> "PageDataBuilder[T]":
        """
        设置记录列表
        
        Args:
            records: 数据记录列表
            
        Returns:
            self (支持链式调用)
        """
        self._records = records
        return self
    
    def total(self, total: int) -> "PageDataBuilder[T]":
        """
        设置总数
        
        Args:
            total: 总记录数
            
        Returns:
            self (支持链式调用)
        """
        self._total = total
        return self
    
    def page_num(self, page_num: int) -> "PageDataBuilder[T]":
        """
        设置页码
        
        Args:
            page_num: 页码
            
        Returns:
            self (支持链式调用)
        """
        self._page_num = page_num
        return self
    
    def page_size(self, page_size: int) -> "PageDataBuilder[T]":
        """
        设置每页大小
        
        Args:
            page_size: 每页大小
            
        Returns:
            self (支持链式调用)
        """
        self._page_size = page_size
        return self
    
    def pagination(self, page_num: int, page_size: int) -> "PageDataBuilder[T]":
        """
        一次性设置分页信息
        
        Args:
            page_num: 页码
            page_size: 每页大小
            
        Returns:
            self (支持链式调用)
        """
        self._page_num = page_num
        self._page_size = page_size
        return self
    
    def build(self) -> PageData[T]:
        """
        构建分页数据对象
        
        Returns:
            PageData 对象
        """
        return PageData(
            records=self._records,
            total=self._total,
            pageNum=self._page_num,
            pageSize=self._page_size
        )
    
    @classmethod
    def from_query_result(
        cls,
        records: list[T],
        total: int,
        page_num: int,
        page_size: int
    ) -> PageData[T]:
        """
        从查询结果创建分页数据
        
        Args:
            records: 数据记录列表
            total: 总记录数
            page_num: 页码
            page_size: 每页大小
            
        Returns:
            PageData 对象
        """
        return (
            cls()
            .records(records)
            .total(total)
            .pagination(page_num, page_size)
            .build()
        )

