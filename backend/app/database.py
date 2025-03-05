"""
数据库连接模块
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from .config import active_config

# 创建数据库引擎
engine = create_engine(active_config.DATABASE_URI)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


def get_db() -> Session:
    """
    获取数据库会话
    
    Returns:
        Session: 数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库"""
    # 导入所有模型以确保它们被注册
    from .models import question
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
