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

