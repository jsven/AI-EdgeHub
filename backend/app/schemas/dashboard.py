"""
仪表盘相关的 Pydantic 模式
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SystemStats(BaseModel):
    """系统统计"""
    cpu_usage: float = Field(..., description="CPU使用率(%)")
    memory_usage: float = Field(..., description="内存使用率(%)")
    total_channels: int = Field(..., description="总通道数")
    active_channels: int = Field(..., description="活跃通道数")
    total_tasks: int = Field(..., description="总任务数")
    running_tasks: int = Field(..., description="运行中任务数")


class ChannelStats(BaseModel):
    """通道统计"""
    channel_id: int
    channel_name: str
    fps: float = Field(..., description="帧率")
    status: str = Field(..., description="状态")
    inference_latency: Optional[float] = Field(None, description="推理延迟(ms)")


class PerformanceData(BaseModel):
    """性能数据"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    inference_latency: float


class AlertRecord(BaseModel):
    """告警记录"""
    id: int
    task_id: int
    task_name: str
    alert_type: str
    content: str
    confidence: Optional[float] = None
    image_url: Optional[str] = None
    created_at: datetime


class DashboardResponse(BaseModel):
    """仪表盘响应"""
    system_stats: SystemStats
    channel_stats: List[ChannelStats]
    recent_alerts: List[AlertRecord]
