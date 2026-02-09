# AI-EdgeHub Backend

AI-EdgeHub 后端服务，基于 FastAPI 构建。

## 功能特性

- 视频流管理（RTSP/RTMP/ONVIF/USB/File）
- AI模型管理（ONNX/OpenVINO/PaddlePaddle）
- 任务配置与调度
- 工业联动（Modbus TCP/MQTT/Webhook）
- 实时监控与告警

## 技术栈

- Python 3.8+
- FastAPI
- SQLAlchemy (异步)
- SQLite
- Redis
- OpenVINO / ONNX Runtime
- OpenCV / FFmpeg

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

### 3. 运行服务

```bash
python -m app.main
```

或使用 uvicorn：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问API文档

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 项目结构

```
backend/
├── app/
│   ├── api/          # API路由
│   ├── core/         # 核心业务逻辑
│   ├── models/       # 数据模型
│   ├── schemas/      # Pydantic模式
│   ├── services/     # 服务层
│   └── utils/        # 工具函数
├── tests/            # 测试文件
└── requirements.txt  # 依赖列表
```

## API端点

### 通道管理
- `GET /api/v1/channels` - 获取通道列表
- `POST /api/v1/channels` - 创建通道
- `GET /api/v1/channels/{id}` - 获取通道详情
- `PUT /api/v1/channels/{id}` - 更新通道
- `DELETE /api/v1/channels/{id}` - 删除通道

### 模型管理
- `GET /api/v1/models` - 获取模型列表
- `POST /api/v1/models` - 上传模型
- `GET /api/v1/models/{id}` - 获取模型详情
- `DELETE /api/v1/models/{id}` - 删除模型

### 任务管理
- `GET /api/v1/tasks` - 获取任务列表
- `POST /api/v1/tasks` - 创建任务
- `GET /api/v1/tasks/{id}` - 获取任务详情
- `PUT /api/v1/tasks/{id}` - 更新任务
- `POST /api/v1/tasks/{id}/start` - 启动任务
- `POST /api/v1/tasks/{id}/stop` - 停止任务

### 仪表盘
- `GET /api/v1/dashboard` - 获取仪表盘数据
- `GET /api/v1/dashboard/stats` - 获取系统统计

## 开发说明

### 数据库迁移

使用 SQLAlchemy 的自动创建表功能，首次运行会自动创建表结构。

### 日志

日志文件保存在 `logs/` 目录下，按日期分割。

### 文件上传

上传的文件保存在 `uploads/` 目录下：
- `uploads/models/` - 模型文件
- `uploads/videos/` - 视频文件
- `uploads/alerts/` - 告警图片
