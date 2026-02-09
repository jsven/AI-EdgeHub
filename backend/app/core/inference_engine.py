"""
推理引擎
"""
import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
from app.core.model_manager import model_manager
from app.utils.logger import logger
import time


class InferenceEngine:
    """推理引擎"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.stats: Dict[int, Dict] = {}  # task_id -> stats
    
    def preprocess_image(self, image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """图像预处理"""
        h, w = target_size
        resized = cv2.resize(image, (w, h))
        normalized = resized.astype(np.float32) / 255.0
        return normalized
    
    def postprocess_detection(
        self, 
        outputs: np.ndarray, 
        image_shape: Tuple[int, int],
        conf_threshold: float = 0.5
    ) -> List[Dict]:
        """
        后处理检测结果
        
        Args:
            outputs: 模型输出
            image_shape: 原始图像尺寸 (h, w)
            conf_threshold: 置信度阈值
            
        Returns:
            检测结果列表
        """
        detections = []
        
        # 假设输出格式为 [batch, num_detections, 6] 或 [num_detections, 6]
        # 格式: [x1, y1, x2, y2, confidence, class_id]
        if len(outputs.shape) == 3:
            outputs = outputs[0]  # 移除batch维度
        
        h, w = image_shape
        
        for detection in outputs:
            if len(detection) >= 6:
                x1, y1, x2, y2, conf, cls_id = detection[:6]
                
                if conf >= conf_threshold:
                    detections.append({
                        "bbox": [float(x1), float(y1), float(x2), float(y2)],
                        "confidence": float(conf),
                        "class_id": int(cls_id),
                        "label": f"class_{int(cls_id)}"  # 默认标签，实际应从模型获取
                    })
        
        return detections
    
    def infer(
        self, 
        model_id: int, 
        image: np.ndarray,
        conf_threshold: float = 0.5
    ) -> Tuple[List[Dict], float]:
        """
        执行推理
        
        Returns:
            (检测结果列表, 推理耗时ms)
        """
        start_time = time.time()
        
        # 获取模型信息
        model_info = model_manager.get_model(model_id)
        if not model_info:
            logger.error(f"模型 {model_id} 未加载")
            return [], 0.0
        
        # 获取输入尺寸
        input_shape = model_info.get("input_shape")
        if input_shape and len(input_shape) >= 3:
            target_h, target_w = int(input_shape[-2]), int(input_shape[-1])
        else:
            target_h, target_w = 640, 640
        
        # 预处理
        preprocessed = self.preprocess_image(image, (target_h, target_w))
        
        # 转换为NCHW格式
        if len(preprocessed.shape) == 3:
            preprocessed = np.transpose(preprocessed, (2, 0, 1))
            preprocessed = np.expand_dims(preprocessed, axis=0)
        
        # 执行推理
        try:
            session = model_info["session"]
            input_name = model_info["input_name"]
            
            if model_info["format"] == "ONNX":
                outputs = session.run(None, {input_name: preprocessed})
            elif model_info["format"] == "OpenVINO":
                outputs = session([preprocessed])
                outputs = [output for output in outputs.values()]
            else:
                return [], 0.0
            
            inference_time = (time.time() - start_time) * 1000  # 转换为ms
            
            # 后处理
            if outputs:
                detections = self.postprocess_detection(
                    outputs[0], 
                    image.shape[:2],
                    conf_threshold
                )
                
                # 更新标签（如果有）
                labels = model_info.get("labels")
                if labels:
                    for det in detections:
                        cls_id = det.get("class_id", 0)
                        if isinstance(labels, list) and cls_id < len(labels):
                            det["label"] = labels[cls_id]
                        elif isinstance(labels, dict):
                            det["label"] = labels.get(str(cls_id), f"class_{cls_id}")
                
                return detections, inference_time
            
            return [], inference_time
            
        except Exception as e:
            logger.error(f"推理失败: {e}")
            return [], (time.time() - start_time) * 1000
    
    def update_stats(self, task_id: int, inference_time: float):
        """更新统计信息"""
        if task_id not in self.stats:
            self.stats[task_id] = {
                "total_inferences": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "min_time": float('inf'),
                "max_time": 0.0
            }
        
        stats = self.stats[task_id]
        stats["total_inferences"] += 1
        stats["total_time"] += inference_time
        stats["avg_time"] = stats["total_time"] / stats["total_inferences"]
        stats["min_time"] = min(stats["min_time"], inference_time)
        stats["max_time"] = max(stats["max_time"], inference_time)
    
    def get_stats(self, task_id: int) -> Optional[Dict]:
        """获取统计信息"""
        return self.stats.get(task_id)


# 全局推理引擎实例
inference_engine = InferenceEngine()
