"""
模型相关的 Pydantic 模式
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ModelBase(BaseModel):
    """模型基础模式"""
    name: str = Field(..., description="模型名称")
    format: str = Field(..., description="模型格式: ONNX/OpenVINO/PaddlePaddle")
    description: Optional[str] = Field(None, description="描述")


class ModelCreate(BaseModel):
    """创建模型模式（上传时使用）"""
    name: str
    format: str
    description: Optional[str] = None


class ModelUpdate(BaseModel):
    """更新模型模式"""
    name: Optional[str] = None
    description: Optional[str] = None


class ModelResponse(ModelBase):
    """模型响应模式"""
    id: int
    file_path: str
    input_size: Optional[str] = None
    labels: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ModelAnalyzeResponse(BaseModel):
    """模型分析响应"""
    input_size: Optional[str] = None
    input_shape: Optional[List[int]] = None
    labels: Optional[List[str]] = None
    format: str
    message: str
