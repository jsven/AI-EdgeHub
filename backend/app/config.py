"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "AI-EdgeHub"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_edgehub.db"
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # 文件存储配置
    UPLOAD_DIR: str = "./uploads"
    MODEL_DIR: str = "./uploads/models"
    VIDEO_DIR: str = "./uploads/videos"
    ALERT_IMAGE_DIR: str = "./uploads/alerts"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # CORS配置
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # 视频流配置
    MAX_CONCURRENT_STREAMS: int = 16
    FRAME_BUFFER_SIZE: int = 10
    DEFAULT_FPS: int = 15
    
    # 推理引擎配置
    INFERENCE_THREADS: int = 4
    INFERENCE_QUEUE_SIZE: int = 100
    
    # 工业联动配置
    MODBUS_TIMEOUT: int = 5
    MQTT_KEEPALIVE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()

# 确保必要的目录存在
os.makedirs(settings.MODEL_DIR, exist_ok=True)
os.makedirs(settings.VIDEO_DIR, exist_ok=True)
os.makedirs(settings.ALERT_IMAGE_DIR, exist_ok=True)
