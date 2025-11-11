"""
AI模型配置服务
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.ai_models import AIModel
from app.models.schemas import AIModelResponse, AIModelCreateRequest, AIModelUpdateRequest
from app.core.exceptions import LiteratureException, NotFoundException


class AIModelService:
    """AI模型配置服务类"""
    
    async def create_model(
        self, 
        db: AsyncSession, 
        user_id: int, 
        request: AIModelCreateRequest
    ) -> AIModel:
        """
        创建AI模型配置
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            request: 创建请求
            
        Returns:
            新创建的AI模型配置
        """
        # 如果设置为默认，先取消其他默认模型
        if request.isDefault:
            await self._clear_default_models(db, user_id)
        
        model = AIModel(
            user_id=user_id,
            name=request.name,
            provider=request.provider,
            base_url=request.baseUrl,
            api_key=request.apiKey,
            model_name=request.modelName,
            max_tokens=request.maxTokens,
            temperature=request.temperature,
            is_default=1 if request.isDefault else 0,
            description=request.description,
            status=1
        )
        
        db.add(model)
        await db.flush()
        await db.refresh(model)
        
        return model
    
    async def get_model_by_id(
        self, 
        db: AsyncSession, 
        model_id: int, 
        user_id: int
    ) -> Optional[AIModel]:
        """
        根据ID获取AI模型配置
        
        Args:
            db: 数据库会话
            model_id: 模型ID
            user_id: 用户ID
            
        Returns:
            AI模型配置或None
        """
        result = await db.execute(
            select(AIModel).where(
                and_(
                    AIModel.id == model_id,
                    AIModel.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_user_models(
        self, 
        db: AsyncSession, 
        user_id: int
    ) -> List[AIModel]:
        """
        获取用户的所有AI模型配置
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            AI模型配置列表
        """
        result = await db.execute(
            select(AIModel)
            .where(AIModel.user_id == user_id)
            .order_by(AIModel.is_default.desc(), AIModel.create_time.desc())
        )
        return list(result.scalars().all())
    
    async def get_default_model(
        self, 
        db: AsyncSession, 
        user_id: int
    ) -> Optional[AIModel]:
        """
        获取用户的默认AI模型
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            默认AI模型配置或None
        """
        result = await db.execute(
            select(AIModel).where(
                and_(
                    AIModel.user_id == user_id,
                    AIModel.is_default == 1,
                    AIModel.status == 1
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def update_model(
        self, 
        db: AsyncSession, 
        model_id: int, 
        user_id: int, 
        request: AIModelUpdateRequest
    ) -> AIModel:
        """
        更新AI模型配置
        
        Args:
            db: 数据库会话
            model_id: 模型ID
            user_id: 用户ID
            request: 更新请求
            
        Returns:
            更新后的AI模型配置
        """
        model = await self.get_model_by_id(db, model_id, user_id)
        if not model:
            raise NotFoundException("AI模型配置不存在")
        
        # 如果设置为默认，先取消其他默认模型
        if request.isDefault is True:
            await self._clear_default_models(db, user_id)
        
        # 更新字段
        if request.name is not None:
            model.name = request.name
        if request.baseUrl is not None:
            model.base_url = request.baseUrl
        if request.apiKey is not None:
            model.api_key = request.apiKey
        if request.modelName is not None:
            model.model_name = request.modelName
        if request.maxTokens is not None:
            model.max_tokens = request.maxTokens
        if request.temperature is not None:
            model.temperature = request.temperature
        if request.isDefault is not None:
            model.is_default = 1 if request.isDefault else 0
        if request.status is not None:
            model.status = request.status
        if request.description is not None:
            model.description = request.description
        
        await db.flush()
        await db.refresh(model)
        
        return model
    
    async def delete_model(
        self, 
        db: AsyncSession, 
        model_id: int, 
        user_id: int
    ) -> bool:
        """
        删除AI模型配置
        
        Args:
            db: 数据库会话
            model_id: 模型ID
            user_id: 用户ID
            
        Returns:
            是否删除成功
        """
        model = await self.get_model_by_id(db, model_id, user_id)
        if not model:
            raise NotFoundException("AI模型配置不存在")
        
        await db.delete(model)
        await db.flush()
        
        return True
    
    async def _clear_default_models(self, db: AsyncSession, user_id: int):
        """清除用户的所有默认模型标记"""
        result = await db.execute(
            select(AIModel).where(
                and_(
                    AIModel.user_id == user_id,
                    AIModel.is_default == 1
                )
            )
        )
        models = result.scalars().all()
        for model in models:
            model.is_default = 0
        await db.flush()
    
    def to_response(self, model: AIModel) -> AIModelResponse:
        """
        转换为响应模型
        
        Args:
            model: AI模型配置对象
            
        Returns:
            AI模型响应模型
        """
        return AIModelResponse(
            id=model.id,
            userId=model.user_id,
            name=model.name,
            provider=model.provider,
            baseUrl=model.base_url,
            apiKey=model.api_key if model.api_key else None,
            modelName=model.model_name,
            maxTokens=model.max_tokens,
            temperature=model.temperature,
            isDefault=model.is_default,
            status=model.status,
            description=model.description,
            createTime=model.create_time,
            updateTime=model.update_time
        )


# 创建全局实例
ai_model_service = AIModelService()

