"""
用户数据模型
"""
from sqlalchemy import Column, BigInteger, String, Integer, Text, DateTime, SmallInteger
from sqlalchemy.sql import func
from app.core.database import Base


class User(Base):
    """用户表模型"""
    __tablename__ = "users"
        
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    username = Column(String(255), nullable=False, unique=True, comment="用户名")
    email = Column(String(255), nullable=False, unique=True, comment="邮箱")
    password = Column(String(255), nullable=False, comment="密码(加密后)")
    role = Column(String(50), default="user", comment="角色: admin, user")
    status = Column(SmallInteger, default=1, comment="状态: 0-禁用, 1-启用")
    create_time = Column(DateTime, default=func.now(), comment="创建时间")
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email}, role={self.role}, status={self.status})>"
    