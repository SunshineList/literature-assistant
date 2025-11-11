"""
Pydantic 数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LiteratureQueryRequest(BaseModel):
    """文献查询请求"""
    pageNum: int = Field(default=1, ge=1, description="页码")
    pageSize: int = Field(default=10, ge=1, le=100, description="每页大小")
    keyword: Optional[str] = Field(default=None, description="关键词")
    tags: Optional[List[str]] = Field(default=None, description="标签列表")
    fileType: Optional[str] = Field(default=None, description="文件类型")
    startDate: Optional[str] = Field(default=None, description="开始日期")
    endDate: Optional[str] = Field(default=None, description="结束日期")


class LiteratureResponse(BaseModel):
    """文献响应模型"""
    id: int
    originalName: str
    filePath: str
    fileSize: int
    fileType: str
    contentLength: int
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    readingGuideSummary: Optional[str] = None
    status: int
    createTime: datetime
    updateTime: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_model(cls, literature):
        """从ORM模型转换"""
        import json
        
        # 解析tags
        tags = None
        if literature.tags:
            try:
                tags = json.loads(literature.tags)
            except:
                tags = []
        
        return cls(
            id=literature.id,
            originalName=literature.original_name,
            filePath=literature.file_path,
            fileSize=literature.file_size,
            fileType=literature.file_type,
            contentLength=literature.content_length,
            tags=tags,
            description=literature.description,
            readingGuideSummary=literature.reading_guide,
            status=literature.status,
            createTime=literature.create_time,
            updateTime=literature.update_time
        )


class LiteratureDetailResponse(LiteratureResponse):
    """文献详情响应模型（包含完整阅读指南）"""
    pass


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "ok"
    message: str = "服务正常运行"


# ==================== 用户相关 ====================

class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, description="密码")


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    role: str
    status: int
    createTime: datetime
    updateTime: datetime

    class Config:
        from_attributes = True


class UserLoginResponse(BaseModel):
    """用户登录响应"""
    token: str
    user: UserResponse


class UserUpdateRequest(BaseModel):
    """用户更新请求"""
    email: Optional[str] = None
    password: Optional[str] = None


# ==================== AI模型配置相关 ====================

class AIModelCreateRequest(BaseModel):
    """AI模型创建请求"""
    name: str = Field(..., min_length=1, max_length=255, description="模型名称")
    provider: str = Field(default="openai_compatible", description="提供商类型")
    baseUrl: str = Field(..., description="API基础URL")
    apiKey: Optional[str] = Field(None, description="API密钥")
    modelName: str = Field(..., description="实际模型名称")
    maxTokens: int = Field(default=4096, ge=1, description="最大token数")
    temperature: str = Field(default="0.7", description="温度参数")
    isDefault: bool = Field(default=False, description="是否为默认模型")
    description: Optional[str] = Field(None, description="模型描述")


class AIModelUpdateRequest(BaseModel):
    """AI模型更新请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="模型名称")
    baseUrl: Optional[str] = Field(None, description="API基础URL")
    apiKey: Optional[str] = Field(None, description="API密钥")
    modelName: Optional[str] = Field(None, description="实际模型名称")
    maxTokens: Optional[int] = Field(None, ge=1, description="最大token数")
    temperature: Optional[str] = Field(None, description="温度参数")
    isDefault: Optional[bool] = Field(None, description="是否为默认模型")
    status: Optional[int] = Field(None, description="状态")
    description: Optional[str] = Field(None, description="模型描述")


class AIModelResponse(BaseModel):
    """AI模型响应"""
    id: int
    userId: int
    name: str
    provider: str
    baseUrl: str
    apiKey: Optional[str] = None
    modelName: str
    maxTokens: int
    temperature: str
    isDefault: int
    status: int
    description: Optional[str] = None
    createTime: datetime
    updateTime: datetime

    class Config:
        from_attributes = True

