"""
MQTT 服务
"""
import json
import asyncio
import paho.mqtt.client as mqtt
from typing import Optional, Callable
from app.utils.logger import logger


class MQTTService:
    """MQTT 服务"""
    
    def __init__(self):
        self.clients: dict[str, mqtt.Client] = {}
        self.lock = asyncio.Lock()
    
    def get_client(
        self,
        broker: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> mqtt.Client:
        """获取或创建MQTT客户端"""
        key = f"{broker}:{port}"
        if key not in self.clients:
            client = mqtt.Client()
            if username and password:
                client.username_pw_set(username, password)
            client.connect(broker, port, keepalive=60)
            client.loop_start()
            self.clients[key] = client
        return self.clients[key]
    
    async def publish(
        self,
        broker: str,
        port: int,
        topic: str,
        payload: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        qos: int = 0
    ) -> bool:
        """发布消息"""
        try:
            client = self.get_client(broker, port, username, password)
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: client.publish(topic, payload, qos=qos)
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"MQTT发布成功: {topic}")
                return True
            else:
                logger.error(f"MQTT发布失败: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"MQTT发布异常: {e}")
            return False
    
    async def subscribe(
        self,
        broker: str,
        port: int,
        topic: str,
        callback: Callable,
        username: Optional[str] = None,
        password: Optional[str] = None,
        qos: int = 0
    ) -> bool:
        """订阅主题"""
        try:
            client = self.get_client(broker, port, username, password)
            
            def on_message(client, userdata, msg):
                try:
                    payload = msg.payload.decode('utf-8')
                    callback(topic, payload)
                except Exception as e:
                    logger.error(f"MQTT消息处理错误: {e}")
            
            client.on_message = on_message
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: client.subscribe(topic, qos=qos)
            )
            
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"MQTT订阅成功: {topic}")
                return True
            else:
                logger.error(f"MQTT订阅失败: {result[0]}")
                return False
                
        except Exception as e:
            logger.error(f"MQTT订阅异常: {e}")
            return False
    
    async def test_connection(
        self,
        broker: str,
        port: int,
        topic: str,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> tuple[bool, str]:
        """测试连接"""
        try:
            client = mqtt.Client()
            if username and password:
                client.username_pw_set(username, password)
            
            connected = False
            
            def on_connect(client, userdata, flags, rc):
                nonlocal connected
                if rc == 0:
                    connected = True
            
            client.on_connect = on_connect
            client.connect(broker, port, keepalive=10)
            client.loop_start()
            
            # 等待连接
            await asyncio.sleep(2)
            
            if connected:
                # 尝试发布测试消息
                result = client.publish(topic, "test", qos=0)
                client.loop_stop()
                client.disconnect()
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    return True, "连接成功"
                else:
                    return False, f"发布测试消息失败: {result.rc}"
            else:
                client.loop_stop()
                client.disconnect()
                return False, "无法连接到MQTT Broker"
                
        except Exception as e:
            return False, f"连接异常: {str(e)}"


# 全局MQTT服务实例
mqtt_service = MQTTService()
