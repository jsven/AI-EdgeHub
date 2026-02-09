"""
告警数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Alert(Base):
    """告警记录模型"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, comment="关联任务ID")
    alert_type = Column(String(50), nullable=False, comment="告警类型")
    content = Column(Text, nullable=True, comment="告警内容")
    confidence = Column(Float, nullable=True, comment="置信度")
    image_path = Column(Text, nullable=True, comment="告警图片路径")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    task = relationship("Task", backref="alerts")
    
    def __repr__(self):
        return f"<Alert(id={self.id}, task_id={self.task_id}, type='{self.alert_type}')>"
