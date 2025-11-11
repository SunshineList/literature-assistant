"""
迁移基类
"""
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession


class Migration(ABC):
    """
    迁移抽象基类
    
    每个迁移文件都应该继承此类并实现 upgrade 和 downgrade 方法
    """
    
    # 迁移版本号（时间戳格式：YYYYMMDDHHMMSS）
    version: str = "00000000000000"
    
    # 迁移描述
    description: str = "未命名迁移"
    
    # 依赖的迁移版本（可选）
    dependencies: list[str] = []
    
    @abstractmethod
    async def upgrade(self, session: AsyncSession):
        """
        执行迁移（升级数据库）
        
        Args:
            session: 数据库会话
        """
        pass
    
    @abstractmethod
    async def downgrade(self, session: AsyncSession):
        """
        回滚迁移（降级数据库）
        
        Args:
            session: 数据库会话
        """
        pass
    
    def __repr__(self):
        return f"<Migration {self.version}: {self.description}>"

