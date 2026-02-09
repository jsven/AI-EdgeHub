"""
Modbus TCP 服务
"""
from pymodbus.client import ModbusTcpClient
from typing import Optional
from app.utils.logger import logger
import asyncio


class ModbusService:
    """Modbus TCP 服务"""
    
    def __init__(self):
        self.clients: dict[str, ModbusTcpClient] = {}
    
    def get_client(self, host: str, port: int) -> ModbusTcpClient:
        """获取或创建Modbus客户端"""
        key = f"{host}:{port}"
        if key not in self.clients:
            client = ModbusTcpClient(host=host, port=port)
            self.clients[key] = client
        return self.clients[key]
    
    async def write_register(
        self,
        host: str,
        port: int,
        slave_id: int,
        address: int,
        value: int,
        timeout: int = 5
    ) -> bool:
        """写入寄存器"""
        try:
            client = self.get_client(host, port)
            
            # 在事件循环中运行同步操作
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: client.write_register(address, value, unit=slave_id)
            )
            
            if result.isError():
                logger.error(f"Modbus写入失败: {result}")
                return False
            
            logger.info(f"Modbus写入成功: {host}:{port}, address={address}, value={value}")
            return True
            
        except Exception as e:
            logger.error(f"Modbus写入异常: {e}")
            return False
    
    async def read_register(
        self,
        host: str,
        port: int,
        slave_id: int,
        address: int,
        timeout: int = 5
    ) -> Optional[int]:
        """读取寄存器"""
        try:
            client = self.get_client(host, port)
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: client.read_holding_registers(address, 1, unit=slave_id)
            )
            
            if result.isError():
                logger.error(f"Modbus读取失败: {result}")
                return None
            
            return result.registers[0] if result.registers else None
            
        except Exception as e:
            logger.error(f"Modbus读取异常: {e}")
            return None
    
    async def test_connection(
        self,
        host: str,
        port: int,
        slave_id: int,
        timeout: int = 5
    ) -> tuple[bool, str]:
        """测试连接"""
        try:
            client = ModbusTcpClient(host=host, port=port, timeout=timeout)
            
            loop = asyncio.get_event_loop()
            connected = await loop.run_in_executor(None, client.connect)
            
            if connected:
                # 尝试读取一个寄存器
                result = await loop.run_in_executor(
                    None,
                    lambda: client.read_holding_registers(0, 1, unit=slave_id)
                )
                client.close()
                
                if not result.isError():
                    return True, "连接成功"
                else:
                    return False, f"读取寄存器失败: {result}"
            else:
                return False, "无法连接到PLC"
                
        except Exception as e:
            return False, f"连接异常: {str(e)}"


# 全局Modbus服务实例
modbus_service = ModbusService()
