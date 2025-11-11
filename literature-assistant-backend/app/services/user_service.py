"""
用户服务
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.users import User
from app.models.schemas import UserResponse, UserRegisterRequest, UserUpdateRequest
from app.utils.auth import hash_password, verify_password, create_access_token
from app.core.exceptions import LiteratureException


class UserService:
    """用户服务类"""
    
    async def register(self, db: AsyncSession, request: UserRegisterRequest) -> User:
        """
        用户注册
        
        Args:
            db: 数据库会话
            request: 注册请求
            
        Returns:
            新创建的用户
            
        Raises:
            LiteratureException: 用户名或邮箱已存在
        """
        # 检查用户名是否存在
        result = await db.execute(
            select(User).where(User.username == request.username)
        )
        if result.scalar_one_or_none():
            raise LiteratureException("用户名已存在", code=400)
        
        # 检查邮箱是否存在
        result = await db.execute(
            select(User).where(User.email == request.email)
        )
        if result.scalar_one_or_none():
            raise LiteratureException("邮箱已存在", code=400)
        
        # 创建用户
        user = User(
            username=request.username,
            email=request.email,
            password=hash_password(request.password),
            role="user",
            status=1
        )
        
        db.add(user)
        await db.flush()
        await db.refresh(user)
        
        return user
    
    async def login(self, db: AsyncSession, username: str, password: str) -> tuple[str, User]:
        """
        用户登录
        
        Args:
            db: 数据库会话
            username: 用户名
            password: 密码
            
        Returns:
            (token, user)
            
        Raises:
            LiteratureException: 用户名或密码错误
        """
        # 查询用户
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise LiteratureException("用户名或密码错误", code=401)
        
        # 验证密码
        if not verify_password(password, user.password):
            raise LiteratureException("用户名或密码错误", code=401)
        
        # 检查用户状态
        if user.status != 1:
            raise LiteratureException("用户已被禁用", code=403)
        
        # 生成 token（sub必须是字符串）
        token = create_access_token(data={"sub": str(user.id)})
        
        return token, user
    
    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """
        根据ID获取用户
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            用户对象或None
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def update_user(
        self, 
        db: AsyncSession, 
        user_id: int, 
        request: UserUpdateRequest
    ) -> User:
        """
        更新用户信息
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            request: 更新请求
            
        Returns:
            更新后的用户
            
        Raises:
            LiteratureException: 用户不存在或邮箱已被使用
        """
        user = await self.get_user_by_id(db, user_id)
        if not user:
            raise LiteratureException("用户不存在", code=404)
        
        # 更新邮箱
        if request.email and request.email != user.email:
            # 检查邮箱是否被使用
            result = await db.execute(
                select(User).where(User.email == request.email, User.id != user_id)
            )
            if result.scalar_one_or_none():
                raise LiteratureException("邮箱已被使用", code=400)
            user.email = request.email
        
        # 更新密码
        if request.password:
            user.password = hash_password(request.password)
        
        await db.flush()
        await db.refresh(user)
        
        return user
    
    def to_response(self, user: User) -> UserResponse:
        """
        转换为响应模型
        
        Args:
            user: 用户对象
            
        Returns:
            用户响应模型
        """
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            status=user.status,
            createTime=user.create_time,
            updateTime=user.update_time
        )


# 创建全局实例
user_service = UserService()

