"""
验证器工具
"""
import re
from typing import Tuple
from urllib.parse import urlparse


def validate_rtsp_url(url: str) -> bool:
    """验证RTSP URL格式"""
    pattern = r'^rtsp://.+'
    return bool(re.match(pattern, url))


def validate_rtmp_url(url: str) -> bool:
    """验证RTMP URL格式"""
    pattern = r'^rtmp://.+'
    return bool(re.match(pattern, url))


def validate_url(url: str) -> bool:
    """验证URL格式"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


from typing import Tuple

def validate_model_format(filename: str) -> Tuple[bool, str]:
    """
    验证模型文件格式
    
    Returns:
        (是否有效, 格式名称)
    """
    ext = filename.split('.')[-1].lower()
    format_map = {
        'onnx': 'ONNX',
        'xml': 'OpenVINO',
        'bin': 'OpenVINO',
        'pdmodel': 'PaddlePaddle'
    }
    
    if ext in format_map:
        return True, format_map[ext]
    return False, 'Unknown'
