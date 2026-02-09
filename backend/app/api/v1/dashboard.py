"""
仪表盘 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.channel import Channel
from app.models.task import Task
from app.models.alert import Alert
from app.schemas.dashboard import (
    DashboardResponse,
    SystemStats,
    ChannelStats,
    AlertRecord
)
from app.utils.logger import logger
import psutil
from datetime import datetime, timedelta

router = APIRouter()


@router.get("", response_model=DashboardResponse)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    """获取仪表盘数据"""
    try:
        # 获取系统统计
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # 获取通道统计
        channel_result = await db.execute(select(Channel))
        channels = channel_result.scalars().all()
        total_channels = len(channels)
        active_channels = len([c for c in channels if c.status == "online"])
        
        # 获取任务统计
        task_result = await db.execute(select(Task))
        tasks = task_result.scalars().all()
        total_tasks = len(tasks)
        running_tasks = len([t for t in tasks if t.status == "running"])
        
        system_stats = SystemStats(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            total_channels=total_channels,
            active_channels=active_channels,
            total_tasks=total_tasks,
            running_tasks=running_tasks
        )
        
        # 获取通道状态统计
        channel_stats = []
        for channel in channels:
            # TODO: 从Redis获取实时FPS和延迟数据
            channel_stats.append(ChannelStats(
                channel_id=channel.id,
                channel_name=channel.name,
                fps=0.0,  # 实际应该从Redis获取
                status=channel.status,
                inference_latency=None  # 实际应该从Redis获取
            ))
        
        # 获取最近告警
        alert_result = await db.execute(
            select(Alert)
            .options(selectinload(Alert.task))
            .order_by(Alert.created_at.desc())
            .limit(5)
        )
        alerts = alert_result.scalars().all()
        
        recent_alerts = []
        for alert in alerts:
            recent_alerts.append(AlertRecord(
                id=alert.id,
                task_id=alert.task_id,
                task_name=alert.task.name if alert.task else "未知任务",
                alert_type=alert.alert_type,
                content=alert.content or "",
                confidence=alert.confidence,
                image_url=f"/api/v1/alerts/{alert.id}/image" if alert.image_path else None,
                created_at=alert.created_at
            ))
        
        return DashboardResponse(
            system_stats=system_stats,
            channel_stats=channel_stats,
            recent_alerts=recent_alerts
        )
    except Exception as e:
        logger.error(f"获取仪表盘数据失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取仪表盘数据失败"
        )


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(db: AsyncSession = Depends(get_db)):
    """获取系统统计"""
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        channel_result = await db.execute(select(Channel))
        channels = channel_result.scalars().all()
        total_channels = len(channels)
        active_channels = len([c for c in channels if c.status == "online"])
        
        task_result = await db.execute(select(Task))
        tasks = task_result.scalars().all()
        total_tasks = len(tasks)
        running_tasks = len([t for t in tasks if t.status == "running"])
        
        return SystemStats(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            total_channels=total_channels,
            active_channels=active_channels,
            total_tasks=total_tasks,
            running_tasks=running_tasks
        )
    except Exception as e:
        logger.error(f"获取系统统计失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取系统统计失败"
        )


@router.get("/performance")
async def get_performance_data(
    hours: int = 1,
    db: AsyncSession = Depends(get_db)
):
    """获取性能数据（历史）"""
    # TODO: 从Redis或时间序列数据库获取历史性能数据
    # 这里返回模拟数据
    return {
        "message": "性能数据功能待实现",
        "data": []
    }
