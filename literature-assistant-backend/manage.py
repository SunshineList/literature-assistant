#!/usr/bin/env python
"""
数据库迁移管理命令行工具

类似 Django 的 manage.py，提供数据库迁移相关命令
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from app.db_migrations.manager import migration_manager


async def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1]
    
    if command == "makemigrations":
        # 创建新的迁移文件
        description = sys.argv[2] if len(sys.argv) > 2 else "auto_migration"
        migration_manager.create_migration(description)
    
    elif command == "migrate":
        # 执行迁移
        target_version = sys.argv[2] if len(sys.argv) > 2 else None
        await migration_manager.migrate(target_version)
    
    elif command == "rollback":
        # 回滚迁移
        steps = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        await migration_manager.rollback(steps)
    
    elif command == "showmigrations":
        # 显示迁移状态
        await migration_manager.show_migrations()
    
    elif command == "help" or command == "--help" or command == "-h":
        print_help()
    
    else:
        print(f"错误: 未知命令 '{command}'")
        print_help()
        sys.exit(1)


def print_help():
    """打印帮助信息"""
    help_text = """
数据库迁移管理工具

用法:
    python manage.py <command> [options]

可用命令:

    makemigrations [description]
        创建新的迁移文件
        示例: python manage.py makemigrations "添加用户表"
    
    migrate [target_version]
        执行迁移，将数据库升级到最新版本或指定版本
        示例: python manage.py migrate
        示例: python manage.py migrate 20241110000000
    
    rollback [steps]
        回滚迁移，默认回滚1步
        示例: python manage.py rollback
        示例: python manage.py rollback 2
    
    showmigrations
        显示所有迁移及其应用状态
        示例: python manage.py showmigrations
    
    help
        显示此帮助信息

示例工作流:

    1. 创建新迁移:
       python manage.py makemigrations "添加新字段"
    
    2. 编辑生成的迁移文件，实现 upgrade() 和 downgrade() 方法
    
    3. 执行迁移:
       python manage.py migrate
    
    4. 如需回滚:
       python manage.py rollback

注意:
    - 迁移文件存放在 app/db_migrations/versions/ 目录
    - 迁移版本号使用时间戳格式 (YYYYMMDDHHMMSS)
    - 每个迁移都应该实现 upgrade 和 downgrade 方法
    """
    print(help_text)


if __name__ == "__main__":
    asyncio.run(main())

