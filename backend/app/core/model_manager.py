"""
模型管理服务
"""
import os
import json
import threading
import cv2
import onnxruntime as ort
from openvino.runtime import Core
from typing import Optional, Dict, List, Tuple
import numpy as np
from app.utils.logger import logger
from app.config import settings


class ModelManager:
    """模型管理器"""
    
    def __init__(self):
        self.models: Dict[int, Dict] = {}
        self.lock = threading.Lock()
    
    def load_model(self, model_id: int, model_path: str, model_format: str) -> bool:
        """加载模型"""
        try:
            model_info = {
                "model_id": model_id,
                "model_path": model_path,
                "format": model_format,
                "session": None,
                "input_shape": None,
                "input_name": None,
                "output_names": None,
                "labels": None
            }
            
            if model_format == "ONNX":
                # 加载ONNX模型
                session = ort.InferenceSession(
                    model_path,
                    providers=['CPUExecutionProvider']
                )
                model_info["session"] = session
                model_info["input_name"] = session.get_inputs()[0].name
                model_info["output_names"] = [out.name for out in session.get_outputs()]
                input_shape = session.get_inputs()[0].shape
                model_info["input_shape"] = input_shape
                
            elif model_format == "OpenVINO":
                # 加载OpenVINO模型
                core = Core()
                model = core.read_model(model_path)
                compiled_model = core.compile_model(model, "CPU")
                model_info["session"] = compiled_model
                input_layer = compiled_model.input(0)
                model_info["input_name"] = input_layer.any_name
                model_info["input_shape"] = list(input_layer.shape)
                model_info["output_names"] = [out.any_name for out in compiled_model.outputs]
                
            else:
                logger.error(f"不支持的模型格式: {model_format}")
                return False
            
            with self.lock:
                self.models[model_id] = model_info
            
            logger.info(f"模型 {model_id} 加载成功")
            return True
            
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            return False
    
    def unload_model(self, model_id: int):
        """卸载模型"""
        with self.lock:
            if model_id in self.models:
                del self.models[model_id]
                logger.info(f"模型 {model_id} 已卸载")
    
    def get_model(self, model_id: int) -> Optional[Dict]:
        """获取模型信息"""
        with self.lock:
            return self.models.get(model_id)
    
    def analyze_model(self, model_path: str, model_format: str) -> Dict:
        """分析模型元数据"""
        try:
            result = {
                "input_size": None,
                "input_shape": None,
                "labels": None,
                "format": model_format,
                "message": "分析成功"
            }
            
            if model_format == "ONNX":
                session = ort.InferenceSession(
                    model_path,
                    providers=['CPUExecutionProvider']
                )
                input_shape = session.get_inputs()[0].shape
                result["input_shape"] = list(input_shape)
                if len(input_shape) >= 3:
                    h, w = input_shape[-2], input_shape[-1]
                    result["input_size"] = f"{int(w)},{int(h)}"
                
            elif model_format == "OpenVINO":
                core = Core()
                model = core.read_model(model_path)
                input_layer = model.input(0)
                input_shape = list(input_layer.shape)
                result["input_shape"] = input_shape
                if len(input_shape) >= 3:
                    h, w = input_shape[-2], input_shape[-1]
                    result["input_size"] = f"{int(w)},{int(h)}"
            
            # 尝试从模型文件同目录读取标签文件
            labels_path = model_path.replace(".onnx", "_labels.json").replace(".xml", "_labels.json")
            if os.path.exists(labels_path):
                with open(labels_path, 'r', encoding='utf-8') as f:
                    labels_data = json.load(f)
                    if isinstance(labels_data, list):
                        result["labels"] = labels_data
                    elif isinstance(labels_data, dict) and "labels" in labels_data:
                        result["labels"] = labels_data["labels"]
            
            return result
            
        except Exception as e:
            logger.error(f"分析模型失败: {e}")
            return {
                "input_size": None,
                "input_shape": None,
                "labels": None,
                "format": model_format,
                "message": f"分析失败: {str(e)}"
            }
    
    def infer(self, model_id: int, image: np.ndarray) -> Optional[np.ndarray]:
        """执行推理"""
        model_info = self.get_model(model_id)
        if not model_info:
            logger.error(f"模型 {model_id} 未加载")
            return None
        
        try:
            session = model_info["session"]
            input_name = model_info["input_name"]
            input_shape = model_info["input_shape"]
            
            # 预处理图像
            if len(input_shape) >= 3:
                target_h, target_w = input_shape[-2], input_shape[-1]
            else:
                target_h, target_w = 640, 640
            
            # Resize图像
            resized = cv2.resize(image, (target_w, target_h))
            
            # 归一化 (假设输入是0-255，需要归一化到0-1)
            normalized = resized.astype(np.float32) / 255.0
            
            # 转换为NCHW格式
            if len(normalized.shape) == 3:
                normalized = np.transpose(normalized, (2, 0, 1))
                normalized = np.expand_dims(normalized, axis=0)
            
            # 执行推理
            if model_info["format"] == "ONNX":
                outputs = session.run(None, {input_name: normalized})
            elif model_info["format"] == "OpenVINO":
                outputs = session([normalized])
                outputs = [output for output in outputs.values()]
            else:
                return None
            
            return outputs[0] if outputs else None
            
        except Exception as e:
            logger.error(f"推理失败: {e}")
            return None


# 全局模型管理器实例
model_manager = ModelManager()
