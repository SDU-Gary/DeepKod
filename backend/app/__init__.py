"""
DeepKod后端应用程序包
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import practice
from .database import init_db


def create_app() -> FastAPI:
    """
    创建FastAPI应用程序
    
    Returns:
        FastAPI: FastAPI应用程序实例
    """
    # 创建应用
    app = FastAPI(
        title="DeepKod API",
        description="大学生一站式代码练习平台API",
        version="0.1.0"
    )
    
    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有来源，生产环境应该限制
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(practice.router)
    
    # 初始化数据库
    init_db()
    
    return app


app = create_app()
