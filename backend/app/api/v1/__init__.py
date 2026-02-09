"""
API v1 路由
"""
from fastapi import APIRouter
from app.api.v1 import channels, models, tasks, dashboard, connectivity

api_router = APIRouter()

api_router.include_router(channels.router, prefix="/channels", tags=["通道管理"])
api_router.include_router(models.router, prefix="/models", tags=["模型管理"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["任务管理"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["仪表盘"])
api_router.include_router(connectivity.router, prefix="/connectivity", tags=["工业互联"])
