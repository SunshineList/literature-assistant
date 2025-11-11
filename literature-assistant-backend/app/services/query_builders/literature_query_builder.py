"""
文献查询构建器 - 使用建造者模式
"""
from typing import List
from sqlalchemy import select, and_, or_, func
from sqlalchemy.sql import Select
from app.models.literature import Literature
from app.models.schemas import LiteratureQueryRequest
from app.utils.date_utils import parse_date


class LiteratureQueryBuilder:
    """
    文献查询构建器
    
    使用建造者模式逐步构建复杂的查询条件
    """
    
    def __init__(self):
        """初始化构建器"""
        self._conditions: List = [Literature.deleted == 0]  # 默认条件
        self._order_by = Literature.create_time.desc()  # 默认排序
        self._offset = 0
        self._limit = 10
    
    def with_keyword(self, keyword: str) -> "LiteratureQueryBuilder":
        """
        添加关键词搜索条件
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            self (支持链式调用)
        """
        if keyword:
            keyword_condition = or_(
                Literature.original_name.like(f"%{keyword}%"),
                Literature.description.like(f"%{keyword}%")
            )
            self._conditions.append(keyword_condition)
        return self
    
    def with_tags(self, tags: List[str]) -> "LiteratureQueryBuilder":
        """
        添加标签过滤条件
        
        Args:
            tags: 标签列表
            
        Returns:
            self (支持链式调用)
        """
        if tags:
            tag_conditions = []
            for tag in tags:
                tag_conditions.append(Literature.tags.like(f"%{tag}%"))
            if tag_conditions:
                self._conditions.append(or_(*tag_conditions))
        return self
    
    def with_file_type(self, file_type: str) -> "LiteratureQueryBuilder":
        """
        添加文件类型过滤条件
        
        Args:
            file_type: 文件类型
            
        Returns:
            self (支持链式调用)
        """
        if file_type:
            self._conditions.append(Literature.file_type == file_type)
        return self
    
    def with_date_range(self, start_date: str = None, end_date: str = None) -> "LiteratureQueryBuilder":
        """
        添加日期范围过滤条件
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            self (支持链式调用)
        """
        if start_date:
            start_dt = parse_date(start_date)
            if start_dt:
                self._conditions.append(Literature.create_time >= start_dt)
        
        if end_date:
            end_dt = parse_date(end_date)
            if end_dt:
                self._conditions.append(Literature.create_time <= end_dt)
        
        return self
    
    def with_user(self, user_id: int) -> "LiteratureQueryBuilder":
        """
        添加用户过滤条件
        
        Args:
            user_id: 用户ID
            
        Returns:
            self (支持链式调用)
        """
        if user_id:
            self._conditions.append(Literature.user_id == user_id)
        return self
    
    def with_pagination(self, page_num: int, page_size: int) -> "LiteratureQueryBuilder":
        """
        添加分页条件
        
        Args:
            page_num: 页码（从1开始）
            page_size: 每页大小
            
        Returns:
            self (支持链式调用)
        """
        self._offset = (page_num - 1) * page_size
        self._limit = page_size
        return self
    
    def order_by_create_time(self, descending: bool = True) -> "LiteratureQueryBuilder":
        """
        按创建时间排序
        
        Args:
            descending: 是否降序
            
        Returns:
            self (支持链式调用)
        """
        self._order_by = Literature.create_time.desc() if descending else Literature.create_time.asc()
        return self
    
    def order_by_update_time(self, descending: bool = True) -> "LiteratureQueryBuilder":
        """
        按更新时间排序
        
        Args:
            descending: 是否降序
            
        Returns:
            self (支持链式调用)
        """
        self._order_by = Literature.update_time.desc() if descending else Literature.update_time.asc()
        return self
    
    def build_count_query(self) -> Select:
        """
        构建计数查询
        
        Returns:
            SQLAlchemy Select 对象
        """
        return select(func.count(Literature.id)).where(and_(*self._conditions))
    
    def build_query(self) -> Select:
        """
        构建完整查询
        
        Returns:
            SQLAlchemy Select 对象
        """
        return (
            select(Literature)
            .where(and_(*self._conditions))
            .order_by(self._order_by)
            .offset(self._offset)
            .limit(self._limit)
        )
    
    @classmethod
    def from_request(cls, query_params: LiteratureQueryRequest) -> "LiteratureQueryBuilder":
        """
        从查询请求对象创建构建器
        
        Args:
            query_params: 查询请求参数
            
        Returns:
            配置好的查询构建器
        """
        builder = cls()
        
        # 链式调用配置所有条件
        builder.with_keyword(query_params.keyword) \
            .with_tags(query_params.tags) \
            .with_file_type(query_params.fileType) \
            .with_date_range(query_params.startDate, query_params.endDate) \
            .with_pagination(query_params.pageNum, query_params.pageSize) \
            .order_by_create_time(descending=True)
        
        return builder
    
    def reset(self) -> "LiteratureQueryBuilder":
        """
        重置构建器
        
        Returns:
            self (支持链式调用)
        """
        self._conditions = [Literature.deleted == 0]
        self._order_by = Literature.create_time.desc()
        self._offset = 0
        self._limit = 10
        return self

