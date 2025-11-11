"""
迁移: 初始化数据库
创建时间: 2024-11-10 00:00:00
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db_migrations.base import Migration


class Migration20241110000000(Migration):
    """
    初始化数据库 - 创建 literature 表
    """
    
    version = "20241110000000"
    description = "初始化数据库 - 创建 literature 表"
    dependencies = []
    
    async def upgrade(self, session: AsyncSession):
        """执行迁移（升级数据库）"""
        # 注意：SQLite 使用 INTEGER PRIMARY KEY AUTOINCREMENT
        # MySQL/PostgreSQL 会自动转换为 BIGINT AUTO_INCREMENT
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS literature (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_name VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_size BIGINT NOT NULL,
                file_type VARCHAR(10) NOT NULL,
                content_length INTEGER DEFAULT 0,
                tags VARCHAR(2000),
                description VARCHAR(2000),
                reading_guide TEXT,
                status TINYINT DEFAULT 1,
                create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted TINYINT DEFAULT 0
            )
        """))
        await session.commit()
    
    async def downgrade(self, session: AsyncSession):
        """回滚迁移（降级数据库）"""
        await session.execute(text("DROP TABLE IF EXISTS literature"))
        await session.commit()

