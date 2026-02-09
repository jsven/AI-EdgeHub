"""
模型管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.model import Model
from app.schemas.model import (
    ModelCreate,
    ModelUpdate,
    ModelResponse,
    ModelAnalyzeResponse
)
from app.config import settings
from app.utils.logger import logger
from app.core.model_manager import model_manager
import os
import shutil
import json

router = APIRouter()


@router.get("", response_model=List[ModelResponse])
async def get_models(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取模型列表"""
    try:
        result = await db.execute(
            select(Model).offset(skip).limit(limit)
        )
        models = result.scalars().all()
        return models
    except Exception as e:
        logger.error(f"获取模型列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取模型列表失败"
        )


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取模型详情"""
    result = await db.execute(
        select(Model).where(Model.id == model_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型不存在"
        )
    return model


@router.post("", response_model=ModelResponse, status_code=status.HTTP_201_CREATED)
async def upload_model(
    file: UploadFile = File(...),
    name: str = None,
    format: str = None,
    description: str = None,
    db: AsyncSession = Depends(get_db)
):
    """上传模型文件"""
    try:
        # 验证文件格式
        allowed_formats = ["onnx", "xml", "bin", "pdmodel"]
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in allowed_formats:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件格式: {file_ext}"
            )
        
        # 确定模型格式
        if format is None:
            if file_ext == "onnx":
                format = "ONNX"
            elif file_ext in ["xml", "bin"]:
                format = "OpenVINO"
            elif file_ext == "pdmodel":
                format = "PaddlePaddle"
            else:
                format = "Unknown"
        
        # 保存文件
        model_name = name or file.filename.split(".")[0]
        file_path = os.path.join(settings.MODEL_DIR, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 创建数据库记录
        model = Model(
            name=model_name,
            file_path=file_path,
            format=format,
            description=description
        )
        db.add(model)
        await db.commit()
        await db.refresh(model)
        
        logger.info(f"上传模型成功: {model.name}")
        return model
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"上传模型失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传模型失败: {str(e)}"
        )


@router.post("/{model_id}/analyze", response_model=ModelAnalyzeResponse)
async def analyze_model(
    model_id: int,
    db: AsyncSession = Depends(get_db)
):
    """分析模型元数据"""
    result = await db.execute(
        select(Model).where(Model.id == model_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型不存在"
        )
    
    try:
        # 调用模型管理服务分析模型
        analyze_data = model_manager.analyze_model(model.file_path, model.format)
        
        analyze_result = ModelAnalyzeResponse(
            input_size=analyze_data.get("input_size"),
            input_shape=analyze_data.get("input_shape"),
            labels=analyze_data.get("labels"),
            format=model.format,
            message=analyze_data.get("message", "分析成功")
        )
        
        # 更新模型信息
        if analyze_result.input_size:
            model.input_size = analyze_result.input_size
        if analyze_result.labels:
            model.labels = json.dumps(analyze_result.labels)
        await db.commit()
        
        return analyze_result
    except Exception as e:
        logger.error(f"分析模型失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"分析模型失败: {str(e)}"
        )


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(
    model_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除模型"""
    result = await db.execute(
        select(Model).where(Model.id == model_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="模型不存在"
        )
    
    # 删除文件
    if os.path.exists(model.file_path):
        os.remove(model.file_path)
    
    await db.delete(model)
    await db.commit()
    logger.info(f"删除模型成功: {model_id}")
    return None
