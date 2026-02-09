"""
任务调度器
"""
import asyncio
import threading
import json
import cv2
from typing import Dict, Optional, List
from app.core.video_stream import video_stream_manager
from app.core.model_manager import model_manager
from app.core.inference_engine import inference_engine
from app.core.rule_engine import rule_engine, ROIConfig
from app.services.modbus_service import modbus_service
from app.services.mqtt_service import mqtt_service
from app.services.webhook_service import webhook_service
from app.utils.logger import logger
from app.models.task import Task
from app.models.alert import Alert
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np
from datetime import datetime


class TaskRunner:
    """任务执行器"""
    
    def __init__(self, task_id: int, task_config: Dict, db: AsyncSession):
        self.task_id = task_id
        self.task_config = task_config
        self.db = db
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.frame_skip_counter = 0
        
    def start(self):
        """启动任务"""
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info(f"任务 {self.task_id} 启动")
    
    def stop(self):
        """停止任务"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info(f"任务 {self.task_id} 停止")
    
    def _run(self):
        """任务执行循环"""
        channel_id = self.task_config.get("channel_id")
        model_id = self.task_config.get("model_id")
        rule_config = self.task_config.get("rule_config", {})
        output_config = self.task_config.get("output_config", {})
        roi_config_data = self.task_config.get("roi_config", [])
        
        # 获取视频流
        stream = video_stream_manager.get_stream(channel_id)
        if not stream:
            logger.error(f"任务 {self.task_id} 视频流不存在")
            return
        
        # 确保视频流运行
        if not stream.is_running:
            stream.start()
        
        # 加载模型
        model_info = model_manager.get_model(model_id)
        if not model_info:
            # 尝试加载模型
            from app.models.model import Model
            # 这里需要从数据库获取模型路径
            logger.error(f"任务 {self.task_id} 模型未加载")
            return
        
        # 解析ROI配置
        roi_configs = []
        if roi_config_data:
            if isinstance(roi_config_data, str):
                roi_config_data = json.loads(roi_config_data)
            for roi_data in roi_config_data:
                roi_configs.append(ROIConfig(
                    roi_type=roi_data.get("type", "polygon"),
                    points=roi_data.get("points", [])
                ))
        
        # 解析规则配置
        if isinstance(rule_config, str):
            rule_config = json.loads(rule_config)
        
        detection_frequency = rule_config.get("detection_frequency", 1)
        
        while self.is_running:
            try:
                import time
                
                # 获取视频帧
                frame = stream.get_latest_frame()
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # 检测频率控制
                self.frame_skip_counter += 1
                if self.frame_skip_counter < detection_frequency:
                    time.sleep(0.033)  # ~30fps
                    continue
                self.frame_skip_counter = 0
                
                # 执行推理
                detections, inference_time = inference_engine.infer(
                    model_id=model_id,
                    image=frame,
                    conf_threshold=rule_config.get("confidence_threshold", 0.5)
                )
                
                # 更新统计
                inference_engine.update_stats(self.task_id, inference_time)
                
                # 应用规则
                filtered_detections, trigger = rule_engine.apply_rules(
                    task_id=self.task_id,
                    detections=detections,
                    roi_configs=roi_configs,
                    rule_config=rule_config
                )
                
                # 如果触发，执行输出动作
                if trigger and filtered_detections:
                    # 在后台线程中执行异步操作
                    import asyncio
                    try:
                        # 尝试获取现有事件循环
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        # 如果没有事件循环，创建新的
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    # 在后台执行
                    asyncio.run_coroutine_threadsafe(
                        self._trigger_output(output_config, filtered_detections, frame),
                        loop
                    )
                
                # 短暂休眠
                time.sleep(0.033)  # ~30fps
                
            except Exception as e:
                logger.error(f"任务 {self.task_id} 执行错误: {e}")
                time.sleep(1)
    
    async def _trigger_output(self, output_config: Dict, detections: List[Dict], frame: np.ndarray):
        """触发输出动作"""
        if not output_config:
            return
        
        if isinstance(output_config, str):
            output_config = json.loads(output_config)
        
        output_type = output_config.get("type")
        config = output_config.get("config", {})
        
        try:
            if output_type == "modbus":
                # Modbus TCP输出
                await modbus_service.write_register(
                    host=config.get("host"),
                    port=config.get("port", 502),
                    slave_id=config.get("slave_id", 1),
                    address=config.get("address", 0),
                    value=config.get("value", 1)
                )
                
            elif output_type == "mqtt":
                # MQTT推送
                await mqtt_service.publish(
                    broker=config.get("broker"),
                    port=config.get("port", 1883),
                    topic=config.get("topic", "/ai-edgehub/alerts"),
                    payload=json.dumps({
                        "task_id": self.task_id,
                        "detections": detections,
                        "timestamp": datetime.now().isoformat()
                    })
                )
                
            elif output_type == "webhook":
                # Webhook请求
                await webhook_service.send(
                    url=config.get("url"),
                    method=config.get("method", "POST"),
                    data={
                        "task_id": self.task_id,
                        "detections": detections,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            
            # 保存告警记录
            await self._save_alert(detections, frame)
            
        except Exception as e:
            logger.error(f"触发输出失败: {e}")
    
    async def _save_alert(self, detections: List[Dict], frame: np.ndarray):
        """保存告警记录"""
        try:
            from app.config import settings
            import os
            
            # 保存告警图片
            alert_dir = settings.ALERT_IMAGE_DIR
            os.makedirs(alert_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = os.path.join(alert_dir, f"alert_{self.task_id}_{timestamp}.jpg")
            
            # 在图片上绘制检测框
            annotated_frame = frame.copy()
            for det in detections:
                if "bbox" in det:
                    bbox = det["bbox"]
                    x1, y1, x2, y2 = map(int, bbox)
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    label = det.get("label", "")
                    conf = det.get("confidence", 0)
                    cv2.putText(
                        annotated_frame,
                        f"{label}: {conf:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2
                    )
            
            cv2.imwrite(image_path, annotated_frame)
            
            # 保存到数据库
            alert = Alert(
                task_id=self.task_id,
                alert_type=detections[0].get("label", "unknown"),
                content=json.dumps(detections),
                confidence=detections[0].get("confidence", 0.0),
                image_path=image_path
            )
            self.db.add(alert)
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"保存告警失败: {e}")


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        self.tasks: Dict[int, TaskRunner] = {}
        self.lock = threading.Lock()
    
    def add_task(self, task_id: int, task_config: Dict, db: AsyncSession):
        """添加任务"""
        with self.lock:
            if task_id in self.tasks:
                logger.warning(f"任务 {task_id} 已存在")
                return
            
            runner = TaskRunner(task_id, task_config, db)
            self.tasks[task_id] = runner
            logger.info(f"添加任务: {task_id}")
    
    def remove_task(self, task_id: int):
        """移除任务"""
        with self.lock:
            if task_id in self.tasks:
                runner = self.tasks[task_id]
                runner.stop()
                del self.tasks[task_id]
                logger.info(f"移除任务: {task_id}")
    
    def start_task(self, task_id: int):
        """启动任务"""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].start()
            else:
                logger.error(f"任务 {task_id} 不存在")
    
    def stop_task(self, task_id: int):
        """停止任务"""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id].stop()
    
    def get_task_status(self, task_id: int) -> Optional[Dict]:
        """获取任务状态"""
        with self.lock:
            if task_id in self.tasks:
                runner = self.tasks[task_id]
                return {
                    "task_id": task_id,
                    "is_running": runner.is_running
                }
        return None


# 全局任务调度器实例
task_scheduler = TaskScheduler()
