"""
WebSocket 实时推送
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from app.utils.logger import logger
import json
import asyncio


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """接受连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket连接建立，当前连接数: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """断开连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket连接断开，当前连接数: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"发送WebSocket消息失败: {e}")
    
    async def broadcast(self, message: dict):
        """广播消息"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"广播消息失败: {e}")
                disconnected.append(connection)
        
        # 移除断开的连接
        for conn in disconnected:
            self.disconnect(conn)


# 全局连接管理器
manager = ConnectionManager()

router = APIRouter()


@router.websocket("/ws/preview/{stream_id}")
async def websocket_preview(websocket: WebSocket, stream_id: int):
    """视频流预览WebSocket"""
    await manager.connect(websocket)
    try:
        from app.core.video_stream import video_stream_manager
        import base64
        import cv2
        
        while True:
            stream = video_stream_manager.get_stream(stream_id)
            if stream:
                frame = stream.get_latest_frame()
                if frame is not None:
                    # 编码为JPEG
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    await manager.send_personal_message({
                        "type": "frame",
                        "stream_id": stream_id,
                        "frame": f"data:image/jpeg;base64,{frame_base64}",
                        "fps": stream.fps
                    }, websocket)
            
            await asyncio.sleep(0.033)  # ~30fps
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket端点"""
    await manager.connect(websocket)
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "subscribe":
                    # 订阅特定频道
                    channel = message.get("channel")
                    logger.info(f"客户端订阅频道: {channel}")
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "channel": channel
                    }, websocket)
                
                elif message_type == "ping":
                    # 心跳响应
                    await manager.send_personal_message({
                        "type": "pong"
                    }, websocket)
                    
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "无效的JSON格式"
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# 推送函数，供其他模块调用
async def broadcast_detection_result(task_id: int, detections: list, frame_data: str = None):
    """广播检测结果"""
    await manager.broadcast({
        "type": "detection_result",
        "task_id": task_id,
        "detections": detections,
        "frame_data": frame_data,
        "timestamp": asyncio.get_event_loop().time()
    })


async def broadcast_system_stats(stats: dict):
    """广播系统统计"""
    await manager.broadcast({
        "type": "system_stats",
        "stats": stats,
        "timestamp": asyncio.get_event_loop().time()
    })


async def broadcast_alert(alert: dict):
    """广播告警"""
    await manager.broadcast({
        "type": "alert",
        "alert": alert,
        "timestamp": asyncio.get_event_loop().time()
    })
