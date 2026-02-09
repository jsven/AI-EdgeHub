"""
文件处理工具
"""
import os
import shutil
from pathlib import Path
from app.config import settings
from app.utils.logger import logger


def ensure_dir_exists(dir_path: str):
    """确保目录存在"""
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def save_uploaded_file(file, destination: str) -> str:
    """
    保存上传的文件
    
    Args:
        file: 上传的文件对象
        destination: 目标路径
        
    Returns:
        保存后的文件路径
    """
    ensure_dir_exists(os.path.dirname(destination))
    with open(destination, "wb") as buffer:
        shutil.copyfileobj(file, buffer)
    logger.info(f"文件保存成功: {destination}")
    return destination


def delete_file(file_path: str) -> bool:
    """
    删除文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否删除成功
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"文件删除成功: {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"删除文件失败: {file_path}, 错误: {e}")
        return False


def get_file_size(file_path: str) -> int:
    """获取文件大小（字节）"""
    if os.path.exists(file_path):
        return os.path.getsize(file_path)
    return 0
