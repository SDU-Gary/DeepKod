"""
配置管理模块，用于管理应用程序的配置信息
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 基础配置
class Config:
    # 应用配置
    APP_NAME = "DeepKod"
    DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # 数据库配置
    DATABASE_URI = os.getenv("DATABASE_URI", "mysql+pymysql://user:password@localhost/deepkod")
    
    # DeepSeek API配置
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")
    
    # Elasticsearch配置
    ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost")
    ELASTICSEARCH_PORT = int(os.getenv("ELASTICSEARCH_PORT", "9200"))
    
    # Redis配置
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    
    # 向量检索配置
    FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "data/kodcode_index.faiss")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2")
    
    # 沙箱配置
    SANDBOX_TIMEOUT = int(os.getenv("SANDBOX_TIMEOUT", "10"))  # 沙箱执行超时时间（秒）
    
    # 缓存配置
    CACHE_EXPIRATION = int(os.getenv("CACHE_EXPIRATION", "3600"))  # 缓存过期时间（秒）


# 开发环境配置
class DevelopmentConfig(Config):
    DEBUG = True


# 测试环境配置
class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    DATABASE_URI = "sqlite:///:memory:"


# 生产环境配置
class ProductionConfig(Config):
    DEBUG = False


# 配置映射
config_by_name = {
    "dev": DevelopmentConfig,
    "test": TestingConfig,
    "prod": ProductionConfig
}

# 获取当前配置
active_config = config_by_name[os.getenv("FLASK_ENV", "dev")]
