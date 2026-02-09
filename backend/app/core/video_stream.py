"""
视频流管理服务
"""
import cv2
import asyncio
import threading
from collections import deque
from typing import Optional, Callable
from app.utils.logger import logger
import numpy as np


class VideoStream:
    """单个视频流实例"""
    
    def __init__(self, stream_id: int, url: str, protocol: str, max_buffer_size: int = 10):
        self.stream_id = stream_id
        self.url = url
        self.protocol = protocol
        self.max_buffer_size = max_buffer_size
        self.frame_buffer = deque(maxlen=max_buffer_size)
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        self.fps = 0.0
        self.frame_count = 0
        self.last_frame_time = None
        
    def start(self):
        """启动视频流"""
        if self.is_running:
            logger.warning(f"视频流 {self.stream_id} 已在运行")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info(f"视频流 {self.stream_id} 启动成功")
    
    def stop(self):
        """停止视频流"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        if self.cap:
            self.cap.release()
            self.cap = None
        logger.info(f"视频流 {self.stream_id} 已停止")
    
    def _run(self):
        """视频流读取循环"""
        retry_count = 0
        max_retries = 5
        
        while self.is_running:
            try:
                # 打开视频流
                if self.cap is None:
                    if self.protocol == "FILE":
                        self.cap = cv2.VideoCapture(self.url)
                    elif self.protocol in ["RTSP", "RTMP"]:
                        self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
                    else:
                        self.cap = cv2.VideoCapture(self.url)
                    
                    if not self.cap.isOpened():
                        raise Exception(f"无法打开视频流: {self.url}")
                    
                    retry_count = 0
                    logger.info(f"视频流 {self.stream_id} 连接成功")
                
                # 读取帧
                ret, frame = self.cap.read()
                if ret:
                    with self.lock:
                        self.frame_buffer.append(frame.copy())
                        self.frame_count += 1
                        # 计算FPS
                        import time
                        current_time = time.time()
                        if self.last_frame_time:
                            elapsed = current_time - self.last_frame_time
                            if elapsed > 0:
                                self.fps = 1.0 / elapsed
                        self.last_frame_time = current_time
                    retry_count = 0
                else:
                    # 读取失败，尝试重连
                    retry_count += 1
                    if retry_count >= max_retries:
                        logger.error(f"视频流 {self.stream_id} 读取失败，尝试重连...")
                        if self.cap:
                            self.cap.release()
                            self.cap = None
                        retry_count = 0
                        import time
                        time.sleep(2)
                    
            except Exception as e:
                logger.error(f"视频流 {self.stream_id} 错误: {e}")
                if self.cap:
                    self.cap.release()
                    self.cap = None
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"视频流 {self.stream_id} 重连失败，停止尝试")
                    break
                import time
                time.sleep(2)
    
    def get_latest_frame(self) -> Optional[np.ndarray]:
        """获取最新帧"""
        with self.lock:
            if self.frame_buffer:
                return self.frame_buffer[-1].copy()
        return None
    
    def get_status(self) -> dict:
        """获取状态信息"""
        with self.lock:
            return {
                "stream_id": self.stream_id,
                "url": self.url,
                "protocol": self.protocol,
                "is_running": self.is_running,
                "fps": self.fps,
                "buffer_size": len(self.frame_buffer),
                "frame_count": self.frame_count
            }


class VideoStreamManager:
    """视频流管理器"""
    
    def __init__(self):
        self.streams: dict[int, VideoStream] = {}
        self.lock = threading.Lock()
    
    def add_stream(self, stream_id: int, url: str, protocol: str) -> VideoStream:
        """添加视频流"""
        with self.lock:
            if stream_id in self.streams:
                logger.warning(f"视频流 {stream_id} 已存在")
                return self.streams[stream_id]
            
            stream = VideoStream(stream_id, url, protocol)
            self.streams[stream_id] = stream
            logger.info(f"添加视频流: {stream_id}")
            return stream
    
    def remove_stream(self, stream_id: int):
        """移除视频流"""
        with self.lock:
            if stream_id in self.streams:
                stream = self.streams[stream_id]
                stream.stop()
                del self.streams[stream_id]
                logger.info(f"移除视频流: {stream_id}")
    
    def get_stream(self, stream_id: int) -> Optional[VideoStream]:
        """获取视频流"""
        with self.lock:
            return self.streams.get(stream_id)
    
    def start_stream(self, stream_id: int):
        """启动视频流"""
        stream = self.get_stream(stream_id)
        if stream:
            stream.start()
        else:
            logger.error(f"视频流 {stream_id} 不存在")
    
    def stop_stream(self, stream_id: int):
        """停止视频流"""
        stream = self.get_stream(stream_id)
        if stream:
            stream.stop()
    
    def get_all_status(self) -> list:
        """获取所有视频流状态"""
        with self.lock:
            return [stream.get_status() for stream in self.streams.values()]
    
    def test_connection(self, url: str, protocol: str, timeout: int = 5) -> tuple[bool, str]:
        """测试视频流连接"""
        try:
            if protocol == "FILE":
                cap = cv2.VideoCapture(url)
            elif protocol in ["RTSP", "RTMP"]:
                cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
            else:
                cap = cv2.VideoCapture(url)
            
            if not cap.isOpened():
                return False, "无法打开视频流"
            
            # 尝试读取一帧
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                return True, "连接成功"
            else:
                return False, "无法读取视频帧"
        except Exception as e:
            return False, f"连接失败: {str(e)}"


# 全局视频流管理器实例
video_stream_manager = VideoStreamManager()
