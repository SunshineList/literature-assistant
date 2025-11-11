"""
AI模型配置数据模型
"""
from sqlalchemy import Column, BigInteger, String, Integer, Text, DateTime, SmallInteger, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base


class AIModel(Base):
    """AI模型配置表"""
    __tablename__ = "ai_models"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, comment="用户ID")
    name = Column(String(255), nullable=False, comment="模型名称（用户自定义）")
    provider = Column(String(50), nullable=False, comment="提供商类型: openai_compatible")
    base_url = Column(String(500), nullable=False, comment="API基础URL")
    api_key = Column(String(500), nullable=True, comment="API密钥")
    model_name = Column(String(255), nullable=False, comment="实际模型名称")
    max_tokens = Column(Integer, default=4096, comment="最大token数")
    temperature = Column(String(10), default="0.7", comment="温度参数")
    is_default = Column(SmallInteger, default=0, comment="是否为默认模型: 0-否, 1-是")
    status = Column(SmallInteger, default=1, comment="状态: 0-禁用, 1-启用")
    description = Column(Text, nullable=True, comment="模型描述")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<AIModel(id={self.id}, name={self.name}, provider={self.provider}, user_id={self.user_id})>"

