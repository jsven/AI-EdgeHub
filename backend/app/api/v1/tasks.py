"""
任务管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.task import Task
from app.models.channel import Channel
from app.models.model import Model
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskControlRequest
)
from app.utils.logger import logger
from app.core.task_scheduler import task_scheduler
from app.core.video_stream import video_stream_manager
from app.core.model_manager import model_manager
import json

router = APIRouter()


@router.get("", response_model=List[TaskResponse])
async def get_tasks(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取任务列表"""
    try:
        result = await db.execute(
            select(Task).offset(skip).limit(limit)
        )
        tasks = result.scalars().all()
        return tasks
    except Exception as e:
        logger.error(f"获取任务列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取任务列表失败"
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取任务详情"""
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    return task


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建任务"""
    try:
        # 验证通道和模型是否存在
        channel_result = await db.execute(
            select(Channel).where(Channel.id == task_data.channel_id)
        )
        if not channel_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="通道不存在"
            )
        
        model_result = await db.execute(
            select(Model).where(Model.id == task_data.model_id)
        )
        if not model_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模型不存在"
            )
        
        # 转换配置为JSON字符串
        task_dict = task_data.model_dump()
        if task_dict.get("roi_config"):
            task_dict["roi_config"] = json.dumps(task_dict["roi_config"])
        if task_dict.get("rule_config"):
            task_dict["rule_config"] = json.dumps(task_dict["rule_config"])
        if task_dict.get("output_config"):
            task_dict["output_config"] = json.dumps(task_dict["output_config"])
        
        task = Task(**task_dict)
        db.add(task)
        await db.commit()
        await db.refresh(task)
        logger.info(f"创建任务成功: {task.name}")
        return task
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"创建任务失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建任务失败: {str(e)}"
        )


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新任务"""
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    update_data = task_data.model_dump(exclude_unset=True)
    
    # 转换配置为JSON字符串
    if "roi_config" in update_data and update_data["roi_config"]:
        update_data["roi_config"] = json.dumps(update_data["roi_config"])
    if "rule_config" in update_data and update_data["rule_config"]:
        update_data["rule_config"] = json.dumps(update_data["rule_config"])
    if "output_config" in update_data and update_data["output_config"]:
        update_data["output_config"] = json.dumps(update_data["output_config"])
    
    for key, value in update_data.items():
        setattr(task, key, value)
    
    await db.commit()
    await db.refresh(task)
    logger.info(f"更新任务成功: {task.name}")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除任务"""
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    await db.delete(task)
    await db.commit()
    logger.info(f"删除任务成功: {task_id}")
    return None


@router.post("/{task_id}/start", response_model=TaskResponse)
async def start_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """启动任务"""
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    if task.status == "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="任务已在运行中"
        )
    
    # 准备任务配置
    task_config = {
        "channel_id": task.channel_id,
        "model_id": task.model_id,
        "roi_config": task.roi_config,
        "rule_config": task.rule_config,
        "output_config": task.output_config
    }
    
    # 确保视频流存在并启动
    channel_result = await db.execute(
        select(Channel).where(Channel.id == task.channel_id)
    )
    channel = channel_result.scalar_one_or_none()
    if channel:
        stream = video_stream_manager.get_stream(task.channel_id)
        if not stream:
            stream = video_stream_manager.add_stream(
                task.channel_id,
                channel.url,
                channel.protocol
            )
        if not stream.is_running:
            stream.start()
    
    # 确保模型已加载
    model_result = await db.execute(
        select(Model).where(Model.id == task.model_id)
    )
    model = model_result.scalar_one_or_none()
    if model:
        model_info = model_manager.get_model(task.model_id)
        if not model_info:
            model_manager.load_model(task.model_id, model.file_path, model.format)
    
    # 添加任务到调度器
    task_scheduler.add_task(task_id, task_config, db)
    
    # 启动任务
    task_scheduler.start_task(task_id)
    
    task.status = "running"
    await db.commit()
    await db.refresh(task)
    logger.info(f"启动任务成功: {task.name}")
    return task


@router.post("/{task_id}/stop", response_model=TaskResponse)
async def stop_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """停止任务"""
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 停止任务
    task_scheduler.stop_task(task_id)
    
    task.status = "stopped"
    await db.commit()
    await db.refresh(task)
    logger.info(f"停止任务成功: {task.name}")
    return task


@router.post("/{task_id}/clone", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def clone_task(
    task_id: int,
    new_name: str,
    db: AsyncSession = Depends(get_db)
):
    """克隆任务"""
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    original_task = result.scalar_one_or_none()
    if not original_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 创建新任务
    new_task = Task(
        name=new_name,
        channel_id=original_task.channel_id,
        model_id=original_task.model_id,
        roi_config=original_task.roi_config,
        rule_config=original_task.rule_config,
        output_config=original_task.output_config,
        description=original_task.description,
        status="stopped"
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    logger.info(f"克隆任务成功: {new_task.name}")
    return new_task
