"""
规则引擎
"""
import numpy as np
from typing import List, Dict, Optional, Tuple
from app.utils.logger import logger
import cv2


class ROIConfig:
    """ROI配置"""
    def __init__(self, roi_type: str, points: List[List[float]]):
        self.type = roi_type  # polygon, rectangle, line
        self.points = np.array(points, dtype=np.float32)
    
    def contains_point(self, x: float, y: float) -> bool:
        """判断点是否在ROI内"""
        if self.type == "polygon":
            return cv2.pointPolygonTest(self.points, (x, y), False) >= 0
        elif self.type == "rectangle":
            if len(self.points) >= 2:
                x1, y1 = self.points[0]
                x2, y2 = self.points[1]
                return x1 <= x <= x2 and y1 <= y <= y2
        elif self.type == "line":
            # 绊线检测：判断点是否在线的某一侧
            if len(self.points) >= 2:
                p1, p2 = self.points[0], self.points[1]
                # 计算点到直线的距离和方向
                return self._point_side_of_line(p1, p2, (x, y))
        return False
    
    def _point_side_of_line(self, p1: Tuple, p2: Tuple, point: Tuple) -> bool:
        """判断点在线的哪一侧"""
        x1, y1 = p1
        x2, y2 = p2
        x, y = point
        # 计算叉积
        cross = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)
        return cross >= 0  # 在线的上方或线上


class RuleEngine:
    """规则引擎"""
    
    def __init__(self):
        self.frame_counters: Dict[int, Dict] = {}  # task_id -> {label: count}
    
    def check_roi(self, detections: List[Dict], roi_configs: List[ROIConfig]) -> List[Dict]:
        """ROI区域过滤"""
        if not roi_configs:
            return detections
        
        filtered = []
        for det in detections:
            # 获取检测框中心点
            if "bbox" in det:
                bbox = det["bbox"]
                center_x = (bbox[0] + bbox[2]) / 2
                center_y = (bbox[1] + bbox[3]) / 2
                
                # 检查是否在任何ROI内
                in_roi = False
                for roi in roi_configs:
                    if roi.contains_point(center_x, center_y):
                        in_roi = True
                        break
                
                if in_roi:
                    filtered.append(det)
            else:
                # 如果没有bbox，默认通过
                filtered.append(det)
        
        return filtered
    
    def filter_by_confidence(self, detections: List[Dict], threshold: float) -> List[Dict]:
        """置信度过滤"""
        return [det for det in detections if det.get("confidence", 0) >= threshold]
    
    def check_consecutive_frames(
        self, 
        task_id: int, 
        label: str, 
        consecutive_frames: int
    ) -> bool:
        """检查连续帧判定"""
        if task_id not in self.frame_counters:
            self.frame_counters[task_id] = {}
        
        counters = self.frame_counters[task_id]
        
        if label not in counters:
            counters[label] = 0
        
        counters[label] += 1
        
        if counters[label] >= consecutive_frames:
            counters[label] = 0  # 重置计数器
            return True
        
        return False
    
    def reset_counters(self, task_id: int):
        """重置计数器"""
        if task_id in self.frame_counters:
            self.frame_counters[task_id] = {}
    
    def apply_rules(
        self,
        task_id: int,
        detections: List[Dict],
        roi_configs: List[ROIConfig],
        rule_config: Dict
    ) -> Tuple[List[Dict], bool]:
        """
        应用规则
        
        Returns:
            (过滤后的检测结果, 是否触发)
        """
        # ROI过滤
        filtered = self.check_roi(detections, roi_configs)
        
        # 置信度过滤
        threshold = rule_config.get("confidence_threshold", 0.5)
        filtered = self.filter_by_confidence(filtered, threshold)
        
        # 检查目标标签
        target_label = rule_config.get("target_label", "")
        if target_label:
            filtered = [det for det in filtered if det.get("label") == target_label]
        
        # 连续帧判定
        trigger = False
        if filtered:
            consecutive_frames = rule_config.get("consecutive_frames", 1)
            if self.check_consecutive_frames(task_id, target_label, consecutive_frames):
                trigger = True
        
        return filtered, trigger


# 全局规则引擎实例
rule_engine = RuleEngine()
