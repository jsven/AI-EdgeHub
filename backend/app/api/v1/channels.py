"""
通道管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.models.channel import Channel
from app.schemas.channel import (
    ChannelCreate,
    ChannelUpdate,
    ChannelResponse,
    ChannelPreviewRequest,
    ChannelPreviewResponse
)
from app.utils.logger import logger
from app.core.video_stream import video_stream_manager

router = APIRouter()


@router.get("", response_model=List[ChannelResponse])
async def get_channels(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取通道列表"""
    try:
        result = await db.execute(
            select(Channel).offset(skip).limit(limit)
        )
        channels = result.scalars().all()
        return channels
    except Exception as e:
        logger.error(f"获取通道列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取通道列表失败"
        )


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取通道详情"""
    result = await db.execute(
        select(Channel).where(Channel.id == channel_id)
    )
    channel = result.scalar_one_or_none()
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通道不存在"
        )
    return channel


@router.post("", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel_data: ChannelCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建通道"""
    try:
        channel = Channel(**channel_data.model_dump())
        db.add(channel)
        await db.commit()
        await db.refresh(channel)
        logger.info(f"创建通道成功: {channel.name}")
        return channel
    except Exception as e:
        await db.rollback()
        logger.error(f"创建通道失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建通道失败"
        )


@router.put("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: int,
    channel_data: ChannelUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新通道"""
    result = await db.execute(
        select(Channel).where(Channel.id == channel_id)
    )
    channel = result.scalar_one_or_none()
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通道不存在"
        )
    
    update_data = channel_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(channel, key, value)
    
    await db.commit()
    await db.refresh(channel)
    logger.info(f"更新通道成功: {channel.name}")
    return channel


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除通道"""
    result = await db.execute(
        select(Channel).where(Channel.id == channel_id)
    )
    channel = result.scalar_one_or_none()
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="通道不存在"
        )
    
    await db.delete(channel)
    await db.commit()
    logger.info(f"删除通道成功: {channel_id}")
    return None


@router.post("/preview", response_model=ChannelPreviewResponse)
async def preview_channel(request: ChannelPreviewRequest):
    """预览视频流"""
    try:
        # 测试视频流连接
        success, message = video_stream_manager.test_connection(
            request.url,
            request.protocol
        )
        
        if success:
            # 创建临时预览流
            preview_id = hash(request.url) % 1000000
            stream = video_stream_manager.add_stream(preview_id, request.url, request.protocol)
            stream.start()
            
            return ChannelPreviewResponse(
                success=True,
                message="预览成功",
                preview_url=f"ws://localhost:8000/ws/preview/{preview_id}"
            )
        else:
            return ChannelPreviewResponse(
                success=False,
                message=message
            )
    except Exception as e:
        logger.error(f"预览通道失败: {e}")
        return ChannelPreviewResponse(
            success=False,
            message=f"预览失败: {str(e)}"
        )


@router.post("/batch-check")
async def batch_check_channels(db: AsyncSession = Depends(get_db)):
    """批量检测通道状态"""
    try:
        result = await db.execute(select(Channel))
        channels = result.scalars().all()
        
        results = []
        for channel in channels:
            # 检测视频流连接
            success, message = video_stream_manager.test_connection(
                channel.url,
                channel.protocol
            )
            
            # 更新通道状态
            channel.status = "online" if success else "offline"
            await db.commit()
            
            results.append({
                "channel_id": channel.id,
                "name": channel.name,
                "status": "online" if success else "offline",
                "message": message
            })
        
        return {"results": results}
    except Exception as e:
        logger.error(f"批量检测通道失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="批量检测失败"
        )
