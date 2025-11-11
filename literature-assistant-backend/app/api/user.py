"""
用户管理 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.response import Response
from app.core.response_builder import ResponseBuilder
from app.core.exceptions import LiteratureException
from app.models.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserLoginResponse,
    UserResponse,
    UserUpdateRequest
)
from app.services.user_service import user_service
from app.utils.auth import get_current_user
from app.models.users import User

router = APIRouter(prefix="/user", tags=["用户管理"])


@router.post("/register", response_model=Response[UserResponse])
async def register(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    用户注册
    """
    try:
        user = await user_service.register(db, request)
        await db.commit()
        
        user_response = user_service.to_response(user)
        return ResponseBuilder.ok(data=user_response, message="注册成功")
    
    except LiteratureException as e:
        return ResponseBuilder.error(message=e.message, code=e.code)
    except Exception as e:
        return ResponseBuilder.error(message=f"注册失败: {str(e)}", code=500)


@router.post("/login", response_model=Response[UserLoginResponse])
async def login(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    用户登录
    """
    try:
        token, user = await user_service.login(db, request.username, request.password)
        
        user_response = user_service.to_response(user)
        login_response = UserLoginResponse(token=token, user=user_response)
        
        return ResponseBuilder.ok(data=login_response, message="登录成功")
    
    except LiteratureException as e:
        return ResponseBuilder.error(message=e.message, code=e.code)
    except Exception as e:
        return ResponseBuilder.error(message=f"登录失败: {str(e)}", code=500)


@router.get("/me", response_model=Response[UserResponse])
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户信息
    """
    try:
        user_response = user_service.to_response(current_user)
        return ResponseBuilder.ok(data=user_response, message="查询成功")
    
    except Exception as e:
        return ResponseBuilder.error(message=f"查询失败: {str(e)}", code=500)


@router.put("/me", response_model=Response[UserResponse])
async def update_current_user(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新当前用户信息
    """
    try:
        user = await user_service.update_user(db, current_user.id, request)
        await db.commit()
        
        user_response = user_service.to_response(user)
        return ResponseBuilder.ok(data=user_response, message="更新成功")
    
    except LiteratureException as e:
        return ResponseBuilder.error(message=e.message, code=e.code)
    except Exception as e:
        return ResponseBuilder.error(message=f"更新失败: {str(e)}", code=500)

