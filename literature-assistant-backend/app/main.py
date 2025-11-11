"""
FastAPI 应用主入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.core.database import init_db
from app.core.exceptions import LiteratureException
from app.core.response import Response
from app.api import literature, user, ai_model
from app.core.response_builder import ResponseBuilder


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("初始化数据库...")
    await init_db()
    print("数据库初始化完成")
    
    yield
    
    # 关闭时执行
    print("应用关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="基于 FastAPI 的文献管理后端服务",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# 全局异常处理
@app.exception_handler(LiteratureException)
async def literature_exception_handler(request: Request, exc: LiteratureException):
    """自定义异常处理"""
    return ResponseBuilder.error(message=exc.message, code=exc.code)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    print(f"未处理的异常: {str(exc)}")
    return Response.error(message=f"服务器内部错误: {str(exc)}", code=500)


# 注册路由
app.include_router(literature.router, prefix=settings.API_PREFIX)
app.include_router(user.router, prefix=settings.API_PREFIX)
app.include_router(ai_model.router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Literature Assistant API",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get(f"{settings.API_PREFIX}/health")
async def health():
    """健康检查"""
    return Response.ok(
        data={"status": "ok", "message": "服务正常运行"},
        message="健康检查通过"
    ).model_dump()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

