"""
通道数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Channel(Base):
    """视频通道模型"""
    __tablename__ = "channels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="通道名称")
    url = Column(Text, nullable=False, comment="视频流地址")
    protocol = Column(String(20), nullable=False, comment="协议类型: RTSP/RTMP/ONVIF/USB/FILE")
    status = Column(String(20), default="offline", comment="状态: online/offline/error")
    description = Column(Text, nullable=True, comment="描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Channel(id={self.id}, name='{self.name}', protocol='{self.protocol}')>"
