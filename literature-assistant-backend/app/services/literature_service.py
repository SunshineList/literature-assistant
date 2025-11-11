"""
文献服务 - 使用建造者模式和仓储模式
"""
import json
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.literature import Literature
from app.models.schemas import LiteratureQueryRequest, LiteratureResponse, LiteratureDetailResponse
from app.core.exceptions import NotFoundException, DatabaseException
from app.services.query_builders.literature_query_builder import LiteratureQueryBuilder


class LiteratureService:
    """
    文献服务
    
    使用建造者模式构建复杂查询
    """
    
    async def create_literature(
        self,
        db: AsyncSession,
        user_id: int,
        original_name: str,
        file_path: str,
        file_size: int,
        file_type: str,
        content_length: int = 0,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None,
        reading_guide: Optional[str] = None,
        status: int = 0
    ) -> Literature:
        """
        创建文献记录
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            original_name: 原始文件名
            file_path: 文件路径
            file_size: 文件大小
            file_type: 文件类型
            content_length: 内容长度
            tags: 标签列表
            description: 描述
            reading_guide: 阅读指南
            status: 状态
            
        Returns:
            文献对象
        """
        try:
            # 序列化tags
            tags_json = json.dumps(tags, ensure_ascii=False) if tags else None
            
            literature = Literature(
                user_id=user_id,
                original_name=original_name,
                file_path=file_path,
                file_size=file_size,
                file_type=file_type,
                content_length=content_length,
                tags=tags_json,
                description=description,
                reading_guide=reading_guide,
                status=status
            )
            
            db.add(literature)
            await db.flush()
            await db.refresh(literature)
            
            return literature
        except Exception as e:
            raise DatabaseException(f"创建文献记录失败: {str(e)}")
    
    async def update_literature(
        self,
        db: AsyncSession,
        literature_id: int,
        **kwargs
    ) -> Literature:
        """
        更新文献记录
        
        Args:
            db: 数据库会话
            literature_id: 文献ID
            **kwargs: 更新的字段
            
        Returns:
            更新后的文献对象
        """
        try:
            # 查询文献
            literature = await self.get_literature_by_id(db, literature_id)
            
            if not literature:
                raise NotFoundException("文献不存在")
            
            # 更新字段
            for key, value in kwargs.items():
                if hasattr(literature, key):
                    # 特殊处理tags
                    if key == 'tags' and isinstance(value, list):
                        value = json.dumps(value, ensure_ascii=False)
                    setattr(literature, key, value)
            
            await db.flush()
            await db.refresh(literature)
            
            return literature
        except NotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"更新文献记录失败: {str(e)}")
    
    async def get_literature_by_id(
        self,
        db: AsyncSession,
        literature_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Literature]:
        """
        根据ID获取文献
        
        Args:
            db: 数据库会话
            literature_id: 文献ID
            user_id: 用户ID（如果提供，则只返回该用户的文献）
            
        Returns:
            文献对象或None
        """
        try:
            conditions = [
                Literature.id == literature_id,
                Literature.deleted == 0
            ]
            
            if user_id is not None:
                conditions.append(Literature.user_id == user_id)
            
            result = await db.execute(
                select(Literature).where(and_(*conditions))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise DatabaseException(f"查询文献失败: {str(e)}")
    
    async def page_query(
        self,
        db: AsyncSession,
        query_params: LiteratureQueryRequest,
        user_id: Optional[int] = None
    ) -> tuple[List[Literature], int]:
        """
        分页查询文献列表 - 使用建造者模式
        
        Args:
            db: 数据库会话
            query_params: 查询参数
            user_id: 用户ID（如果提供，则只返回该用户的文献）
            
        Returns:
            (文献列表, 总数)
        """
        try:
            # 使用建造者模式构建查询
            query_builder = LiteratureQueryBuilder.from_request(query_params)
            
            # 如果提供了user_id，添加用户过滤条件
            if user_id is not None:
                query_builder.with_user(user_id)
            
            # 查询总数
            count_query = query_builder.build_count_query()
            total_result = await db.execute(count_query)
            total = total_result.scalar()
            
            # 查询数据
            data_query = query_builder.build_query()
            result = await db.execute(data_query)
            literatures = result.scalars().all()
            
            return list(literatures), total
        
        except Exception as e:
            raise DatabaseException(f"查询文献列表失败: {str(e)}")
    
    def to_response(self, literature: Literature) -> LiteratureResponse:
        """转换为响应模型"""
        return LiteratureResponse.from_orm_model(literature)
    
    def to_detail_response(self, literature: Literature) -> LiteratureDetailResponse:
        """转换为详情响应模型"""
        return LiteratureDetailResponse.from_orm_model(literature)
    
    async def delete_literature(
        self,
        db: AsyncSession,
        literature_id: int,
        user_id: int
    ) -> bool:
        """
        删除文献（真删除：删除数据库记录和本地文件）
        
        Args:
            db: 数据库会话
            literature_id: 文献ID
            user_id: 用户ID
            
        Returns:
            是否删除成功
        """
        try:
            literature = await self.get_literature_by_id(db, literature_id, user_id)
            
            if not literature:
                raise NotFoundException("文献不存在或无权限删除")
            
            # 获取文件路径
            file_path = literature.file_path
            
            # 从数据库中删除记录
            await db.delete(literature)
            await db.flush()
            
            # 删除本地文件
            if file_path:
                import os
                from app.config import settings
                
                # 构建完整的文件路径
                full_path = os.path.join(settings.UPLOAD_DIR, file_path)
                
                # 如果文件存在，删除它
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                        print(f"已删除文件: {full_path}")
                    except Exception as e:
                        print(f"删除文件失败: {full_path}, 错误: {str(e)}")
                        # 文件删除失败不影响数据库删除
            
            return True
        except NotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"删除文献失败: {str(e)}")


# 创建全局实例
literature_service = LiteratureService()
