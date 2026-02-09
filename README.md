# AI-EdgeHub 边缘智能中台系统

## 项目简介

AI-EdgeHub 是一个通用的 AI 视觉中间件平台，向下兼容传统 RTSP/ONVIF 摄像头及工业相机，向上支持加载多种深度学习模型（如 PaddlePaddle, ONNX），实现视频流实时抓取、AI 推理分析及结果下发，赋予传统安防设备"大脑"。

## 核心价值

- **利旧升级：** 无需更换摄像头，通过增加边缘主机实现 AI 功能
- **降本增效：** 针对 Intel CPU 进行极致优化，无需昂贵显卡
- **极速部署：** 模块化设计，新场景部署周期从月级缩短至天级

## 技术架构

### 后端技术栈
- Python 3.8+ / FastAPI
- SQLite / Redis
- OpenVINO / ONNX Runtime
- OpenCV / FFmpeg

### 前端技术栈
- Vue 3.3+ / Element Plus
- Pinia / Vue Router
- Axios / Socket.io-client
- ECharts

## 项目结构

```
AI-EdgeHub/
├── backend/          # 后端服务
│   ├── app/         # 应用代码
│   ├── requirements.txt
│   └── README.md
├── frontend/         # 前端应用
│   ├── src/
│   ├── package.json
│   └── README.md
├── docs/            # 文档
│   ├── 产品设计-实现.md
│   ├── 详细设计.md
│   ├── 技术架构设计.md
│   └── 功能详细说明.md
└── README.md
```

## 快速开始

### 后端启动

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 文件配置环境变量
python -m app.main
```

访问 API 文档: http://localhost:8000/api/docs

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

访问前端应用: http://localhost:5173

## 核心功能

### 1. 视频流管理
- 支持 RTSP、RTMP、ONVIF、USB、本地文件接入
- 视频流预览和状态检测
- 批量通道管理

### 2. 模型管理
- 支持 ONNX、OpenVINO、PaddlePaddle 模型格式
- 模型上传和分析
- 模型元数据提取

### 3. 任务配置
- 三步向导创建任务
- ROI 区域配置（待实现）
- 规则引擎配置
- 任务启动/停止/克隆

### 4. 工业联动
- Modbus TCP 配置
- MQTT 消息推送
- Webhook HTTP 请求
- 模拟触发测试

### 5. 实时监控
- 系统性能监控（CPU、内存）
- 通道状态统计
- 最近告警记录

## 文档说明

- [操作手册](docs/操作手册.md) - **用户操作指南，快速上手指南**
- [部署实施文档](docs/部署实施文档.md) - **系统部署实施指南，包含多种部署方案**
- [产品设计文档](docs/产品设计-实现.md) - 产品需求和技术规范
- [详细设计文档](docs/详细设计.md) - UI/UX 设计和交互逻辑
- [技术架构设计](docs/技术架构设计.md) - 系统架构和技术选型
- [功能详细说明](docs/功能详细说明.md) - 功能模块详细说明
- [实现总结](docs/实现总结.md) - 核心功能实现总结

## 开发计划

### 已完成
- ✅ 项目基础架构搭建
- ✅ 后端 API 接口实现
- ✅ 前端页面实现
- ✅ 数据库模型设计
- ✅ 技术文档编写

### 待实现
- ⏳ 视频流管理服务
- ⏳ 模型管理服务
- ⏳ 推理引擎实现
- ⏳ 任务调度器实现
- ⏳ 规则引擎实现
- ⏳ ROI 绘制功能
- ⏳ WebSocket 实时推送
- ⏳ Docker 容器化部署

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。
