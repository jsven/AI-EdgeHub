#!/usr/bin/env python3
"""
数据库初始化脚本
用于手动初始化数据库表结构
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import init_db
from app.utils.logger import logger


async def main():
    """初始化数据库"""
    try:
        logger.info("开始初始化数据库...")
        await init_db()
        logger.info("数据库初始化完成！")
        print("✓ 数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        print(f"✗ 数据库初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
