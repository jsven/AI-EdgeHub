"""
任务相关的 Pydantic 模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ROIConfig(BaseModel):
    """ROI配置"""
    type: str = Field(..., description="类型: polygon/rectangle/line")
    points: List[List[float]] = Field(..., description="坐标点列表")


class RuleConfig(BaseModel):
    """规则配置"""
    target_label: str = Field(..., description="目标标签")
    confidence_threshold: float = Field(..., description="置信度阈值")
    consecutive_frames: int = Field(default=1, description="连续帧数")
    detection_frequency: int = Field(default=1, description="检测频率（每N帧检测一次）")


class OutputConfig(BaseModel):
    """输出配置"""
    type: str = Field(..., description="类型: modbus/mqtt/webhook/tcp")
    config: Dict[str, Any] = Field(..., description="具体配置")


class TaskBase(BaseModel):
    """任务基础模式"""
    name: str = Field(..., description="任务名称")
    channel_id: int = Field(..., description="通道ID")
    model_id: int = Field(..., description="模型ID")
    roi_config: Optional[List[ROIConfig]] = Field(None, description="ROI配置列表")
    rule_config: Optional[RuleConfig] = Field(None, description="规则配置")
    output_config: Optional[OutputConfig] = Field(None, description="输出配置")
    description: Optional[str] = Field(None, description="描述")


class TaskCreate(TaskBase):
    """创建任务模式"""
    pass


class TaskUpdate(BaseModel):
    """更新任务模式"""
    name: Optional[str] = None
    channel_id: Optional[int] = None
    model_id: Optional[int] = None
    roi_config: Optional[List[ROIConfig]] = None
    rule_config: Optional[RuleConfig] = None
    output_config: Optional[OutputConfig] = None
    description: Optional[str] = None


class TaskResponse(TaskBase):
    """任务响应模式"""
    id: int
    status: str = Field(..., description="状态: running/stopped/paused")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskControlRequest(BaseModel):
    """任务控制请求"""
    action: str = Field(..., description="动作: start/stop/pause/resume")
