"""
数据库迁移：添加AI模型配置表
创建时间: 2025-11-11
"""
from sqlalchemy import text
from app.db_migrations.base import Migration


class AddAIModelsTableMigration(Migration):
    """添加AI模型配置表迁移"""
    
    version = "20251111100000"
    description = "添加AI模型配置表，支持用户自定义多个AI模型"
    
    async def upgrade(self, db):
        """升级数据库"""
        # 1. 创建AI模型配置表
        await db.execute(text("""
            CREATE TABLE IF NOT EXISTS ai_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name VARCHAR(255) NOT NULL,
                provider VARCHAR(50) NOT NULL DEFAULT 'openai_compatible',
                base_url VARCHAR(500) NOT NULL,
                api_key VARCHAR(500),
                model_name VARCHAR(255) NOT NULL,
                max_tokens INTEGER DEFAULT 4096,
                temperature VARCHAR(10) DEFAULT '0.7',
                is_default INTEGER DEFAULT 0,
                status INTEGER DEFAULT 1,
                description TEXT,
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))
        
        # 2. 创建索引
        await db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_ai_models_user_id ON ai_models(user_id)
        """))
        await db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_ai_models_is_default ON ai_models(user_id, is_default)
        """))
        
        # 3. 为admin用户创建一些预设模型
        await db.execute(text("""
            INSERT INTO ai_models (user_id, name, provider, base_url, model_name, max_tokens, description, is_default)
            VALUES 
                (1, 'Ollama本地', 'openai_compatible', 'http://localhost:11434/v1', 'qwq:32b', 8192, '本地Ollama服务', 1),
                (1, '通义千问', 'openai_compatible', 'https://dashscope.aliyuncs.com/compatible-mode/v1', 'qwen-plus', 8192, '阿里云通义千问模型', 0),
                (1, 'DeepSeek', 'openai_compatible', 'https://api.deepseek.com', 'deepseek-chat', 8192, 'DeepSeek对话模型', 0),
                (1, 'Kimi', 'openai_compatible', 'https://api.moonshot.cn/v1', 'moonshot-v1-8k', 8192, 'Moonshot Kimi模型', 0)
        """))
        
        await db.commit()
        print("✓ AI模型配置表创建完成")
    
    async def downgrade(self, db):
        """降级数据库"""
        # 删除AI模型配置表
        await db.execute(text("DROP TABLE IF EXISTS ai_models"))
        
        await db.commit()
        print("✓ AI模型配置表已删除")

