"""
应用启动脚本
"""
import uvicorn
from app.config import settings


if __name__ == "__main__":
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║          Literature Assistant API Server                ║
    ║                                                          ║
    ║  Version: {settings.VERSION:<43} ║
    ║  Host:    {settings.HOST:<43} ║
    ║  Port:    {settings.PORT:<43} ║
    ║                                                          ║
    ║  API 文档: http://{settings.HOST}:{settings.PORT}/docs{' ' * 24}║
    ║  健康检查: http://{settings.HOST}:{settings.PORT}{settings.API_PREFIX}/health{' ' * 15}║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

