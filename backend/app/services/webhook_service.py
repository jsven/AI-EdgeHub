"""
Webhook 服务
"""
import json
import aiohttp
from typing import Optional, Dict, Any
from app.utils.logger import logger


class WebhookService:
    """Webhook 服务"""
    
    async def send(
        self,
        url: str,
        method: str = "POST",
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 10
    ) -> bool:
        """发送Webhook请求"""
        try:
            if headers is None:
                headers = {"Content-Type": "application/json"}
            
            async with aiohttp.ClientSession() as session:
                if method.upper() == "POST":
                    async with session.post(
                        url,
                        json=data,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=timeout)
                    ) as response:
                        if response.status == 200:
                            logger.info(f"Webhook发送成功: {url}")
                            return True
                        else:
                            logger.error(f"Webhook发送失败: {url}, status={response.status}")
                            return False
                elif method.upper() == "GET":
                    async with session.get(
                        url,
                        params=data,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=timeout)
                    ) as response:
                        if response.status == 200:
                            logger.info(f"Webhook发送成功: {url}")
                            return True
                        else:
                            logger.error(f"Webhook发送失败: {url}, status={response.status}")
                            return False
                else:
                    logger.error(f"不支持的HTTP方法: {method}")
                    return False
                    
        except Exception as e:
            logger.error(f"Webhook发送异常: {e}")
            return False


# 全局Webhook服务实例
webhook_service = WebhookService()
