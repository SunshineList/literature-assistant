"""
文献数据模型
"""
from sqlalchemy import Column, BigInteger, String, Integer, Text, DateTime, SmallInteger, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class Literature(Base):
    """文献表模型"""
    __tablename__ = "literature"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment="用户ID")
    original_name = Column(String(255), nullable=False, comment="原始文件名")
    file_path = Column(String(500), nullable=False, comment="文件存储路径")
    file_size = Column(BigInteger, nullable=False, comment="文件大小(字节)")
    file_type = Column(String(10), nullable=False, comment="文件类型")
    content_length = Column(Integer, default=0, comment="内容长度")
    tags = Column(String(2000), nullable=True, comment="标签(JSON数组)")
    description = Column(String(2000), nullable=True, comment="描述")
    reading_guide = Column(Text, nullable=True, comment="阅读指南")
    status = Column(SmallInteger, default=1, comment="状态: 0-处理中, 1-已完成, 2-失败")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    deleted = Column(SmallInteger, default=0, comment="删除标记: 0-未删除, 1-已删除")

    def __repr__(self):
        return f"<Literature(id={self.id}, name={self.original_name})>"

