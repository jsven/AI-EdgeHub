"""
任务数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Task(Base):
    """AI任务配置模型"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="任务名称")
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False, comment="关联通道ID")
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False, comment="关联模型ID")
    roi_config = Column(Text, nullable=True, comment="ROI区域配置，JSON格式")
    rule_config = Column(Text, nullable=True, comment="规则配置，JSON格式")
    output_config = Column(Text, nullable=True, comment="输出配置，JSON格式")
    status = Column(String(20), default="stopped", comment="状态: running/stopped/paused")
    description = Column(Text, nullable=True, comment="描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    channel = relationship("Channel", backref="tasks")
    model = relationship("Model", backref="tasks")
    
    def __repr__(self):
        return f"<Task(id={self.id}, name='{self.name}', status='{self.status}')>"
