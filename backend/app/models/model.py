"""
模型数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Model(Base):
    """AI模型文件模型"""
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="模型名称")
    file_path = Column(Text, nullable=False, comment="模型文件路径")
    format = Column(String(20), nullable=False, comment="模型格式: ONNX/OpenVINO/PaddlePaddle")
    input_size = Column(String(50), nullable=True, comment="输入尺寸，如: 640,640")
    labels = Column(Text, nullable=True, comment="标签列表，JSON格式")
    description = Column(Text, nullable=True, comment="描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Model(id={self.id}, name='{self.name}', format='{self.format}')>"
