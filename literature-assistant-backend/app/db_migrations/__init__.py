"""
数据库迁移模块 - 类似 Django migrations

可复用的 FastAPI 数据库迁移工具
"""
from app.db_migrations.manager import MigrationManager
from app.db_migrations.base import Migration

__all__ = ["MigrationManager", "Migration"]

