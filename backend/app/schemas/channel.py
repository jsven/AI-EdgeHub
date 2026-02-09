"""
通道相关的 Pydantic 模式
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChannelBase(BaseModel):
    """通道基础模式"""
    name: str = Field(..., description="通道名称")
    url: str = Field(..., description="视频流地址")
    protocol: str = Field(..., description="协议类型: RTSP/RTMP/ONVIF/USB/FILE")
    description: Optional[str] = Field(None, description="描述")


class ChannelCreate(ChannelBase):
    """创建通道模式"""
    pass


class ChannelUpdate(BaseModel):
    """更新通道模式"""
    name: Optional[str] = None
    url: Optional[str] = None
    protocol: Optional[str] = None
    description: Optional[str] = None


class ChannelResponse(ChannelBase):
    """通道响应模式"""
    id: int
    status: str = Field(..., description="状态: online/offline/error")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChannelPreviewRequest(BaseModel):
    """通道预览请求"""
    url: str
    protocol: str


class ChannelPreviewResponse(BaseModel):
    """通道预览响应"""
    success: bool
    message: str
    preview_url: Optional[str] = None
