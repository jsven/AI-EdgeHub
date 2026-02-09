# AI-EdgeHub Frontend

AI-EdgeHub 前端应用，基于 Vue 3 + Element Plus 构建。

## 功能特性

- 仪表盘实时监控
- 通道管理（视频流接入）
- 模型中心（AI模型管理）
- 任务配置（ROI、规则引擎）
- 工业互联设置（Modbus/MQTT/Webhook）

## 技术栈

- Vue 3.3+ (Composition API)
- Vue Router 4
- Pinia (状态管理)
- Element Plus (UI组件库)
- Axios (HTTP客户端)
- ECharts (图表)
- Socket.io-client (WebSocket)

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 开发模式运行

```bash
npm run dev
```

访问 http://localhost:5173

### 3. 构建生产版本

```bash
npm run build
```

## 项目结构

```
frontend/
├── src/
│   ├── api/          # API接口封装
│   ├── assets/        # 静态资源
│   ├── components/    # 公共组件
│   ├── router/        # 路由配置
│   ├── store/         # 状态管理
│   ├── utils/         # 工具函数
│   ├── views/         # 页面组件
│   └── styles/        # 样式文件
├── public/            # 公共静态文件
└── vite.config.js     # Vite配置
```

## 页面说明

### 仪表盘 (Dashboard)
- 系统性能监控（CPU、内存）
- 通道状态统计
- 最近告警记录

### 通道管理 (ChannelManagement)
- 视频流通道列表
- 新增/编辑/删除通道
- 视频流预览
- 批量检测通道状态

### 模型中心 (ModelHub)
- 模型文件列表
- 上传模型文件
- 模型元数据分析
- 删除模型

### 任务配置 (TaskConfig)
- 任务列表
- 创建/编辑任务
- 三步向导配置：
  1. 选择资源（通道、模型）
  2. 配置ROI区域
  3. 设置规则（置信度、连续帧等）
- 启动/停止任务
- 克隆任务

### 工业互联 (Connectivity)
- Modbus TCP 配置
- MQTT 配置
- Webhook 配置
- 模拟触发测试

## 开发说明

### API代理

开发环境下，API请求会自动代理到后端服务（http://localhost:8000），配置在 `vite.config.js` 中。

### 环境变量

可以创建 `.env` 文件配置环境变量：

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 注意事项

- 确保后端服务已启动
- WebSocket连接需要后端支持
- 视频预览功能需要后端实现视频流转发
