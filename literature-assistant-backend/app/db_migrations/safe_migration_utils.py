"""
安全的数据库迁移工具
提供数据验证、备份保留和回滚机制
"""
from sqlalchemy import text
from typing import Optional


class SafeMigrationHelper:
    """安全迁移辅助类"""
    
    @staticmethod
    async def rebuild_table_with_backup(
        db,
        table_name: str,
        new_table_sql: str,
        data_transfer_sql: str,
        indexes_sql: list[str],
        keep_backup: bool = True
    ):
        """
        安全地重建表（SQLite专用）
        
        Args:
            db: 数据库会话
            table_name: 表名
            new_table_sql: 新表的CREATE TABLE语句
            data_transfer_sql: 数据迁移的INSERT语句
            indexes_sql: 索引创建语句列表
            keep_backup: 是否保留备份表（生产环境建议保留）
        
        Returns:
            备份表名
        """
        backup_table = f"{table_name}_backup_{SafeMigrationHelper._get_timestamp()}"
        
        try:
            print(f"\n⚠️  开始重建表 '{table_name}'...")
            
            # 1. 验证原表存在
            result = await db.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"))
            if not result.scalar():
                print(f"   ⚠️  表 '{table_name}' 不存在，跳过迁移")
                return None
            
            # 2. 统计原表记录数
            result = await db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            original_count = result.scalar()
            print(f"   📊 原表记录数: {original_count}")
            
            # 3. 创建备份表
            await db.execute(text(f"CREATE TABLE {backup_table} AS SELECT * FROM {table_name}"))
            print(f"   ✓ 已创建备份表: {backup_table}")
            
            # 4. 验证备份
            result = await db.execute(text(f"SELECT COUNT(*) FROM {backup_table}"))
            backup_count = result.scalar()
            if backup_count != original_count:
                raise Exception(f"❌ 备份验证失败！原表 {original_count} 条，备份 {backup_count} 条")
            print(f"   ✓ 备份验证通过: {backup_count} 条记录")
            
            # 5. 删除旧表
            await db.execute(text(f"DROP TABLE {table_name}"))
            print(f"   ✓ 已删除旧表: {table_name}")
            
            # 6. 创建新表
            await db.execute(text(new_table_sql))
            print(f"   ✓ 已创建新表结构")
            
            # 7. 迁移数据
            await db.execute(text(data_transfer_sql))
            print(f"   ✓ 数据迁移完成")
            
            # 8. 验证数据迁移
            result = await db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            new_count = result.scalar()
            if new_count != original_count:
                raise Exception(f"❌ 数据迁移验证失败！原表 {original_count} 条，新表 {new_count} 条")
            print(f"   ✓ 数据验证通过: {new_count} 条记录")
            
            # 9. 创建索引
            for idx, index_sql in enumerate(indexes_sql, 1):
                await db.execute(text(index_sql))
            print(f"   ✓ 已创建 {len(indexes_sql)} 个索引")
            
            # 10. 决定是否保留备份
            if keep_backup:
                print(f"   ⚠️  备份表 '{backup_table}' 已保留")
                print(f"   💡 验证命令: SELECT COUNT(*) FROM {backup_table};")
                print(f"   💡 对比命令: SELECT * FROM {backup_table} LIMIT 5;")
                print(f"   💡 删除命令: DROP TABLE {backup_table};")
            else:
                await db.execute(text(f"DROP TABLE {backup_table}"))
                print(f"   ✓ 已删除备份表")
                backup_table = None
            
            print(f"✅ 表 '{table_name}' 重建完成\n")
            return backup_table
            
        except Exception as e:
            print(f"\n❌ 表 '{table_name}' 迁移失败: {str(e)}")
            print(f"   🔄 正在尝试从备份恢复...")
            
            try:
                # 尝试恢复
                await db.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                await db.execute(text(f"ALTER TABLE {backup_table} RENAME TO {table_name}"))
                print(f"   ✓ 已从备份 '{backup_table}' 恢复")
            except Exception as restore_error:
                print(f"   ❌ 自动恢复失败: {str(restore_error)}")
                print(f"   ⚠️  请手动执行以下命令恢复:")
                print(f"      DROP TABLE IF EXISTS {table_name};")
                print(f"      ALTER TABLE {backup_table} RENAME TO {table_name};")
            
            raise
    
    @staticmethod
    async def verify_table_structure(db, table_name: str, expected_columns: list[str]) -> bool:
        """
        验证表结构
        
        Args:
            db: 数据库会话
            table_name: 表名
            expected_columns: 期望的列名列表
        
        Returns:
            是否符合预期
        """
        cursor = await db.execute(text(f"PRAGMA table_info({table_name})"))
        columns = cursor.fetchall()
        actual_columns = [col[1] for col in columns]
        
        missing = set(expected_columns) - set(actual_columns)
        extra = set(actual_columns) - set(expected_columns)
        
        if missing or extra:
            print(f"   ⚠️  表结构不符:")
            if missing:
                print(f"      缺少列: {missing}")
            if extra:
                print(f"      多余列: {extra}")
            return False
        
        return True
    
    @staticmethod
    async def check_foreign_key_constraints(db, table_name: str):
        """检查外键约束"""
        result = await db.execute(text(f"PRAGMA foreign_key_check({table_name})"))
        violations = result.fetchall()
        if violations:
            print(f"   ⚠️  外键约束违规: {len(violations)} 条")
            for v in violations[:5]:  # 只显示前5条
                print(f"      {v}")
            return False
        return True
    
    @staticmethod
    def _get_timestamp() -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d%H%M%S")
    
    @staticmethod
    async def cleanup_old_backups(db, table_name: str, keep_latest: int = 3):
        """
        清理旧的备份表
        
        Args:
            db: 数据库会话
            table_name: 原表名
            keep_latest: 保留最新的N个备份
        """
        # 查找所有备份表
        result = await db.execute(text(f"""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name LIKE '{table_name}_backup_%'
            ORDER BY name DESC
        """))
        backups = [row[0] for row in result.fetchall()]
        
        if len(backups) > keep_latest:
            to_delete = backups[keep_latest:]
            print(f"\n🧹 清理旧备份表 (保留最新 {keep_latest} 个):")
            for backup in to_delete:
                await db.execute(text(f"DROP TABLE {backup}"))
                print(f"   ✓ 已删除: {backup}")
            await db.commit()


class PostgreSQLMigrationHelper:
    """PostgreSQL/MySQL 迁移辅助类（支持ALTER TABLE）"""
    
    @staticmethod
    async def add_column_safe(
        db,
        table_name: str,
        column_name: str,
        column_type: str,
        nullable: bool = True,
        default: Optional[str] = None
    ):
        """
        安全地添加列（PostgreSQL/MySQL）
        
        Args:
            db: 数据库会话
            table_name: 表名
            column_name: 列名
            column_type: 列类型
            nullable: 是否可空
            default: 默认值
        """
        # 检查列是否已存在
        # PostgreSQL
        result = await db.execute(text(f"""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name='{table_name}' AND column_name='{column_name}'
        """))
        
        if result.scalar():
            print(f"   ⚠️  列 '{column_name}' 已存在，跳过")
            return
        
        # 构建ALTER TABLE语句
        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        
        if not nullable:
            sql += " NOT NULL"
        
        if default is not None:
            sql += f" DEFAULT {default}"
        
        await db.execute(text(sql))
        print(f"   ✓ 已添加列: {column_name}")
    
    @staticmethod
    async def drop_column_safe(db, table_name: str, column_name: str):
        """安全地删除列（PostgreSQL/MySQL）"""
        await db.execute(text(f"ALTER TABLE {table_name} DROP COLUMN IF EXISTS {column_name}"))
        print(f"   ✓ 已删除列: {column_name}")

