"""
自定义异常模块
"""


class LiteratureException(Exception):
    """文献助手基础异常"""
    def __init__(self, message: str = "操作失败", code: int = 500):
        self.message = message
        self.code = code
        super().__init__(self.message)


class FileException(LiteratureException):
    """文件相关异常"""
    def __init__(self, message: str = "文件处理失败"):
        super().__init__(message, 400)


class AIException(LiteratureException):
    """AI服务异常"""
    def __init__(self, message: str = "AI服务异常"):
        super().__init__(message, 500)


class DatabaseException(LiteratureException):
    """数据库异常"""
    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(message, 500)


class NotFoundException(LiteratureException):
    """资源未找到异常"""
    def __init__(self, message: str = "资源未找到"):
        super().__init__(message, 404)

