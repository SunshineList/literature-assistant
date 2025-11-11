"""
数据库迁移：删除用户表中的旧AI配置字段
创建时间: 2025-11-11
"""
from sqlalchemy import text
from app.db_migrations.base import Migration


class RemoveOldAIConfigFieldsMigration(Migration):
    """删除用户表中的旧AI配置字段迁移"""
    
    version = "20251111110000"
    description = "删除用户表中的旧AI配置字段(ai_provider, ollama_base_url, ollama_model, kimi_api_key)"
    
    async def upgrade(self, db):
        """升级数据库 - SQLite不支持DROP COLUMN，需要重建表"""
        # 1. 创建新的用户表
        await db.execute(text("""
            CREATE TABLE users_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(255) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) DEFAULT 'user',
                status INTEGER DEFAULT 1,
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # 2. 复制数据（只复制需要的字段）
        await db.execute(text("""
            INSERT INTO users_new (id, username, email, password, role, status, create_time, update_time)
            SELECT id, username, email, password, role, status, create_time, update_time
            FROM users
        """))
        
        # 3. 删除旧表
        await db.execute(text("DROP TABLE users"))
        
        # 4. 重命名新表
        await db.execute(text("ALTER TABLE users_new RENAME TO users"))
        
        # 5. 重建索引
        await db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)
        """))
        await db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        """))
        
        await db.commit()
        print("✓ 已删除用户表中的旧AI配置字段")
    
    async def downgrade(self, db):
        """降级数据库 - 恢复旧字段"""
        # 1. 创建带旧字段的表
        await db.execute(text("""
            CREATE TABLE users_old (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(255) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) DEFAULT 'user',
                status INTEGER DEFAULT 1,
                ai_provider VARCHAR(50) DEFAULT 'ollama',
                ollama_base_url VARCHAR(500),
                ollama_model VARCHAR(255),
                kimi_api_key VARCHAR(500),
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # 2. 复制数据
        await db.execute(text("""
            INSERT INTO users_old (id, username, email, password, role, status, create_time, update_time)
            SELECT id, username, email, password, role, status, create_time, update_time
            FROM users
        """))
        
        # 3. 删除新表
        await db.execute(text("DROP TABLE users"))
        
        # 4. 重命名
        await db.execute(text("ALTER TABLE users_old RENAME TO users"))
        
        # 5. 重建索引
        await db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)
        """))
        await db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        """))
        
        await db.commit()
        print("✓ 已恢复用户表中的旧AI配置字段")

