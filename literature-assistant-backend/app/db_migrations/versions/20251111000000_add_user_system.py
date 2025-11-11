"""
数据库迁移：添加用户系统
创建时间: 2025-11-11
"""
from sqlalchemy import text
from app.db_migrations.base import Migration


class AddUserSystemMigration(Migration):
    """添加用户系统迁移"""
    
    version = "20251111000000"
    description = "添加用户系统，包括用户表和文献表的user_id字段"
    
    async def upgrade(self, db):
        """升级数据库"""
        # 1. 创建用户表
        await db.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
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
        
        # 2. 创建索引
        await db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)
        """))
        await db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        """))
        
        # 3. 创建默认管理员用户 (密码: admin123)
        await db.execute(text("""
            INSERT OR IGNORE INTO users (username, email, password, role, status)
            VALUES ('admin', 'admin@example.com', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin', 1)
        """))
        
        # 4. 检查 literature 表是否已有 user_id 字段
        cursor = await db.execute(text("PRAGMA table_info(literature)"))
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # 5. 如果没有 user_id 字段，则添加
        if 'user_id' not in column_names:
            # SQLite 不支持直接添加外键，需要重建表
            # 先备份数据
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS literature_backup AS 
                SELECT * FROM literature
            """))
            
            # 删除旧表
            await db.execute(text("DROP TABLE IF EXISTS literature"))
            
            # 创建新表（包含 user_id）
            await db.execute(text("""
                CREATE TABLE literature (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL DEFAULT 1,
                    original_name VARCHAR(255) NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    file_size INTEGER NOT NULL,
                    file_type VARCHAR(10) NOT NULL,
                    content_length INTEGER DEFAULT 0,
                    tags VARCHAR(2000),
                    description VARCHAR(2000),
                    reading_guide TEXT,
                    status INTEGER DEFAULT 1,
                    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    deleted INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """))
            
            # 恢复数据（将所有现有文献关联到管理员用户）
            await db.execute(text("""
                INSERT INTO literature 
                (id, user_id, original_name, file_path, file_size, file_type, 
                 content_length, tags, description, reading_guide, status, 
                 create_time, update_time, deleted)
                SELECT 
                    id, 1 as user_id, original_name, file_path, file_size, file_type,
                    content_length, tags, description, reading_guide, status,
                    create_time, update_time, deleted
                FROM literature_backup
            """))
            
            # 删除备份表
            await db.execute(text("DROP TABLE IF EXISTS literature_backup"))
            
            # 创建索引
            await db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_literature_user_id ON literature(user_id)
            """))
            await db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_literature_status ON literature(status)
            """))
            await db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_literature_deleted ON literature(deleted)
            """))
        
        await db.commit()
        print("✓ 用户系统迁移完成")
    
    async def downgrade(self, db):
        """降级数据库"""
        # 1. 备份 literature 数据
        await db.execute(text("""
            CREATE TABLE IF NOT EXISTS literature_backup AS 
            SELECT id, original_name, file_path, file_size, file_type, 
                   content_length, tags, description, reading_guide, status, 
                   create_time, update_time, deleted
            FROM literature
        """))
        
        # 2. 删除新表
        await db.execute(text("DROP TABLE IF EXISTS literature"))
        
        # 3. 重建旧表（不包含 user_id）
        await db.execute(text("""
            CREATE TABLE literature (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_name VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_size INTEGER NOT NULL,
                file_type VARCHAR(10) NOT NULL,
                content_length INTEGER DEFAULT 0,
                tags VARCHAR(2000),
                description VARCHAR(2000),
                reading_guide TEXT,
                status INTEGER DEFAULT 1,
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                deleted INTEGER DEFAULT 0
            )
        """))
        
        # 4. 恢复数据
        await db.execute(text("""
            INSERT INTO literature 
            SELECT * FROM literature_backup
        """))
        
        # 5. 删除备份表
        await db.execute(text("DROP TABLE IF EXISTS literature_backup"))
        
        # 6. 删除用户表
        await db.execute(text("DROP TABLE IF EXISTS users"))
        
        await db.commit()
        print("✓ 用户系统迁移已回滚")

