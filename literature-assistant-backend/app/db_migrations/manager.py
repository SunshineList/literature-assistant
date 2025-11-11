"""
迁移管理器
"""
import os
import importlib
import inspect
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Type
from sqlalchemy import text, Table, Column, String, DateTime, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.db_migrations.base import Migration
from app.core.database import async_session_maker, engine


class MigrationManager:
    """
    数据库迁移管理器
    
    提供类似 Django 的 makemigrations 和 migrate 功能
    """
    
    def __init__(self, migrations_dir: str = None):
        """
        初始化迁移管理器
        
        Args:
            migrations_dir: 迁移文件目录，默认为 app/db_migrations/versions
        """
        if migrations_dir is None:
            current_dir = Path(__file__).parent
            migrations_dir = current_dir / "versions"
        
        self.migrations_dir = Path(migrations_dir)
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
        
        # 迁移历史表名
        self.history_table_name = "migration_history"
    
    async def _ensure_history_table(self, session: AsyncSession):
        """确保迁移历史表存在"""
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.history_table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version VARCHAR(50) NOT NULL UNIQUE,
            description TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        await session.execute(text(create_table_sql))
        await session.commit()
    
    async def _get_applied_migrations(self, session: AsyncSession) -> List[str]:
        """获取已应用的迁移版本列表"""
        await self._ensure_history_table(session)
        
        result = await session.execute(
            text(f"SELECT version FROM {self.history_table_name} ORDER BY version")
        )
        return [row[0] for row in result.fetchall()]
    
    async def _mark_migration_applied(
        self,
        session: AsyncSession,
        version: str,
        description: str
    ):
        """标记迁移为已应用"""
        await session.execute(
            text(f"""
                INSERT INTO {self.history_table_name} (version, description)
                VALUES (:version, :description)
            """),
            {"version": version, "description": description}
        )
        await session.commit()
    
    async def _unmark_migration(self, session: AsyncSession, version: str):
        """取消迁移标记"""
        await session.execute(
            text(f"DELETE FROM {self.history_table_name} WHERE version = :version"),
            {"version": version}
        )
        await session.commit()
    
    def _discover_migrations(self) -> List[Type[Migration]]:
        """
        发现所有迁移类
        
        Returns:
            迁移类列表，按版本号排序
        """
        migrations = []
        
        # 遍历 versions 目录下的所有 Python 文件
        for file_path in self.migrations_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
            
            # 动态导入模块
            module_name = f"app.db_migrations.versions.{file_path.stem}"
            try:
                module = importlib.import_module(module_name)
                
                # 查找 Migration 子类
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, Migration) and 
                        obj is not Migration and
                        hasattr(obj, 'version')):
                        migrations.append(obj)
            except Exception as e:
                print(f"警告: 无法加载迁移文件 {file_path}: {e}")
        
        # 按版本号排序
        migrations.sort(key=lambda m: m.version)
        return migrations
    
    async def show_migrations(self):
        """显示所有迁移及其状态"""
        async with async_session_maker() as session:
            applied = await self._get_applied_migrations(session)
            all_migrations = self._discover_migrations()
            
            print("\n" + "=" * 70)
            print("数据库迁移状态")
            print("=" * 70)
            
            if not all_migrations:
                print("未找到任何迁移文件")
                return
            
            for migration_class in all_migrations:
                migration = migration_class()
                status = "✓ 已应用" if migration.version in applied else "✗ 未应用"
                print(f"{status} | {migration.version} | {migration.description}")
            
            print("=" * 70 + "\n")
    
    async def migrate(self, target_version: Optional[str] = None):
        """
        执行迁移
        
        Args:
            target_version: 目标版本，None 表示迁移到最新版本
        """
        async with async_session_maker() as session:
            applied = await self._get_applied_migrations(session)
            all_migrations = self._discover_migrations()
            
            if not all_migrations:
                print("未找到任何迁移文件")
                return
            
            # 确定需要执行的迁移
            pending_migrations = [
                m for m in all_migrations
                if m.version not in applied
            ]
            
            if target_version:
                # 迁移到指定版本
                pending_migrations = [
                    m for m in pending_migrations
                    if m.version <= target_version
                ]
            
            if not pending_migrations:
                print("✓ 数据库已是最新状态")
                return
            
            print(f"\n准备执行 {len(pending_migrations)} 个迁移:")
            for migration_class in pending_migrations:
                migration = migration_class()
                print(f"  - {migration.version}: {migration.description}")
            
            print()
            
            # 执行迁移
            for migration_class in pending_migrations:
                migration = migration_class()
                print(f"正在应用迁移 {migration.version}: {migration.description}...", end=" ")
                
                try:
                    await migration.upgrade(session)
                    await self._mark_migration_applied(
                        session,
                        migration.version,
                        migration.description
                    )
                    print("✓ 完成")
                except Exception as e:
                    print(f"✗ 失败: {e}")
                    await session.rollback()
                    raise
            
            print(f"\n✓ 成功应用 {len(pending_migrations)} 个迁移\n")
    
    async def rollback(self, steps: int = 1):
        """
        回滚迁移
        
        Args:
            steps: 回滚步数
        """
        async with async_session_maker() as session:
            applied = await self._get_applied_migrations(session)
            
            if not applied:
                print("没有可回滚的迁移")
                return
            
            # 获取要回滚的迁移
            to_rollback = applied[-steps:]
            all_migrations = self._discover_migrations()
            
            print(f"\n准备回滚 {len(to_rollback)} 个迁移:")
            for version in reversed(to_rollback):
                migration_class = next(
                    (m for m in all_migrations if m.version == version),
                    None
                )
                if migration_class:
                    migration = migration_class()
                    print(f"  - {migration.version}: {migration.description}")
            
            print()
            
            # 执行回滚
            for version in reversed(to_rollback):
                migration_class = next(
                    (m for m in all_migrations if m.version == version),
                    None
                )
                
                if not migration_class:
                    print(f"警告: 未找到版本 {version} 的迁移类")
                    continue
                
                migration = migration_class()
                print(f"正在回滚迁移 {migration.version}: {migration.description}...", end=" ")
                
                try:
                    await migration.downgrade(session)
                    await self._unmark_migration(session, migration.version)
                    print("✓ 完成")
                except Exception as e:
                    print(f"✗ 失败: {e}")
                    await session.rollback()
                    raise
            
            print(f"\n✓ 成功回滚 {len(to_rollback)} 个迁移\n")
    
    def create_migration(self, description: str = "auto_migration"):
        """
        创建新的迁移文件
        
        Args:
            description: 迁移描述
        """
        # 生成版本号（时间戳）
        version = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # 生成文件名
        filename = f"{version}_{description.replace(' ', '_')}.py"
        file_path = self.migrations_dir / filename
        
        # 生成迁移文件内容
        content = f'''"""
迁移: {description}
创建时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db_migrations.base import Migration


class Migration{version}(Migration):
    """
    {description}
    """
    
    version = "{version}"
    description = "{description}"
    dependencies = []  # 依赖的迁移版本列表
    
    async def upgrade(self, session: AsyncSession):
        """
        执行迁移（升级数据库）
        
        示例:
        await session.execute(text("""
            CREATE TABLE example (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100)
            )
        """))
        await session.commit()
        """
        # TODO: 在这里编写升级逻辑
        pass
    
    async def downgrade(self, session: AsyncSession):
        """
        回滚迁移（降级数据库）
        
        示例:
        await session.execute(text("DROP TABLE example"))
        await session.commit()
        """
        # TODO: 在这里编写降级逻辑
        pass
'''
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✓ 创建迁移文件: {filename}")
        print(f"  路径: {file_path}")
        print(f"  版本: {version}")
        print(f"\n请编辑文件并实现 upgrade() 和 downgrade() 方法\n")
        
        return file_path


# 创建全局实例
migration_manager = MigrationManager()

