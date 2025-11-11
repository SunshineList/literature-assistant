"""
AI模型配置管理 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.response import Response
from app.core.response_builder import ResponseBuilder
from app.core.exceptions import LiteratureException, NotFoundException
from app.models.schemas import (
    AIModelCreateRequest,
    AIModelUpdateRequest,
    AIModelResponse
)
from app.models.users import User
from app.services.ai_model_service import ai_model_service
from app.utils.auth import get_current_user
from typing import List

router = APIRouter(prefix="/ai-models", tags=["AI模型配置"])


@router.post("", response_model=Response[AIModelResponse])
async def create_ai_model(
    request: AIModelCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    创建AI模型配置
    """
    try:
        model = await ai_model_service.create_model(db, current_user.id, request)
        await db.commit()
        
        response = ai_model_service.to_response(model)
        return ResponseBuilder.ok(data=response, message="创建成功")
    
    except LiteratureException as e:
        return ResponseBuilder.error(message=e.message, code=e.code)
    except Exception as e:
        return ResponseBuilder.error(message=f"创建失败: {str(e)}", code=500)


@router.get("", response_model=Response[List[AIModelResponse]])
async def get_user_ai_models(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的所有AI模型配置
    """
    try:
        models = await ai_model_service.get_user_models(db, current_user.id)
        
        responses = [ai_model_service.to_response(model) for model in models]
        return ResponseBuilder.ok(data=responses, message="查询成功")
    
    except Exception as e:
        return ResponseBuilder.error(message=f"查询失败: {str(e)}", code=500)


@router.get("/default", response_model=Response[AIModelResponse])
async def get_default_ai_model(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的默认AI模型
    """
    try:
        model = await ai_model_service.get_default_model(db, current_user.id)
        
        if not model:
            return ResponseBuilder.not_found(message="未设置默认模型")
        
        response = ai_model_service.to_response(model)
        return ResponseBuilder.ok(data=response, message="查询成功")
    
    except Exception as e:
        return ResponseBuilder.error(message=f"查询失败: {str(e)}", code=500)


@router.get("/{model_id}", response_model=Response[AIModelResponse])
async def get_ai_model(
    model_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取AI模型配置详情
    """
    try:
        model = await ai_model_service.get_model_by_id(db, model_id, current_user.id)
        
        if not model:
            raise NotFoundException("AI模型配置不存在")
        
        response = ai_model_service.to_response(model)
        return ResponseBuilder.ok(data=response, message="查询成功")
    
    except NotFoundException as e:
        return ResponseBuilder.not_found(message=e.message)
    except Exception as e:
        return ResponseBuilder.error(message=f"查询失败: {str(e)}", code=500)


@router.put("/{model_id}", response_model=Response[AIModelResponse])
async def update_ai_model(
    model_id: int,
    request: AIModelUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新AI模型配置
    """
    try:
        model = await ai_model_service.update_model(db, model_id, current_user.id, request)
        await db.commit()
        
        response = ai_model_service.to_response(model)
        return ResponseBuilder.ok(data=response, message="更新成功")
    
    except NotFoundException as e:
        return ResponseBuilder.not_found(message=e.message)
    except LiteratureException as e:
        return ResponseBuilder.error(message=e.message, code=e.code)
    except Exception as e:
        return ResponseBuilder.error(message=f"更新失败: {str(e)}", code=500)


@router.delete("/{model_id}", response_model=Response[bool])
async def delete_ai_model(
    model_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除AI模型配置
    """
    try:
        await ai_model_service.delete_model(db, model_id, current_user.id)
        await db.commit()
        
        return ResponseBuilder.ok(data=True, message="删除成功")
    
    except NotFoundException as e:
        return ResponseBuilder.not_found(message=e.message)
    except LiteratureException as e:
        return ResponseBuilder.error(message=e.message, code=e.code)
    except Exception as e:
        return ResponseBuilder.error(message=f"删除失败: {str(e)}", code=500)

