-- ============================================
-- AI-EdgeHub 数据库表结构定义
-- 数据库类型: MySQL 5.7+ / MariaDB 10.3+
-- 版本: 1.0.0
-- 创建日期: 2024-01-01
-- ============================================

-- 创建数据库（如果不存在）
-- CREATE DATABASE IF NOT EXISTS ai_edgehub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE ai_edgehub;

-- ============================================
-- 1. 通道表 (channels)
-- 存储视频流通道配置信息
-- ============================================
CREATE TABLE IF NOT EXISTS channels (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '通道ID',
    name VARCHAR(100) NOT NULL COMMENT '通道名称',
    url TEXT NOT NULL COMMENT '视频流地址',
    protocol VARCHAR(20) NOT NULL COMMENT '协议类型: RTSP/RTMP/ONVIF/USB/FILE',
    status VARCHAR(20) DEFAULT 'offline' COMMENT '状态: online/offline/error',
    description TEXT COMMENT '描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_channels_status (status),
    INDEX idx_channels_protocol (protocol),
    INDEX idx_channels_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='视频通道表';

-- ============================================
-- 2. 模型表 (models)
-- 存储AI模型文件信息
-- ============================================
CREATE TABLE IF NOT EXISTS models (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '模型ID',
    name VARCHAR(100) NOT NULL COMMENT '模型名称',
    file_path TEXT NOT NULL COMMENT '模型文件路径',
    format VARCHAR(20) NOT NULL COMMENT '模型格式: ONNX/OpenVINO/PaddlePaddle',
    input_size VARCHAR(50) COMMENT '输入尺寸，如: 640,640',
    labels TEXT COMMENT '标签列表，JSON格式',
    description TEXT COMMENT '描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_models_format (format),
    INDEX idx_models_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI模型表';

-- ============================================
-- 3. 任务表 (tasks)
-- 存储AI任务配置信息
-- ============================================
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '任务ID',
    name VARCHAR(100) NOT NULL COMMENT '任务名称',
    channel_id INT NOT NULL COMMENT '关联通道ID',
    model_id INT NOT NULL COMMENT '关联模型ID',
    roi_config TEXT COMMENT 'ROI区域配置，JSON格式',
    rule_config TEXT COMMENT '规则配置，JSON格式',
    output_config TEXT COMMENT '输出配置，JSON格式',
    status VARCHAR(20) DEFAULT 'stopped' COMMENT '状态: running/stopped/paused',
    description TEXT COMMENT '描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE RESTRICT,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE RESTRICT,
    INDEX idx_tasks_channel_id (channel_id),
    INDEX idx_tasks_model_id (model_id),
    INDEX idx_tasks_status (status),
    INDEX idx_tasks_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI任务表';

-- ============================================
-- 4. 告警表 (alerts)
-- 存储告警记录信息
-- ============================================
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '告警ID',
    task_id INT NOT NULL COMMENT '关联任务ID',
    alert_type VARCHAR(50) NOT NULL COMMENT '告警类型',
    content TEXT COMMENT '告警内容',
    confidence FLOAT COMMENT '置信度',
    image_path TEXT COMMENT '告警图片路径',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    INDEX idx_alerts_task_id (task_id),
    INDEX idx_alerts_alert_type (alert_type),
    INDEX idx_alerts_created_at (created_at),
    INDEX idx_alerts_confidence (confidence)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='告警记录表';

-- ============================================
-- 数据库结构说明
-- ============================================
-- 
-- 表关系说明：
-- 1. channels (通道) 1:N tasks (任务)
-- 2. models (模型) 1:N tasks (任务)
-- 3. tasks (任务) 1:N alerts (告警)
--
-- 外键约束：
-- - tasks.channel_id -> channels.id (RESTRICT: 删除通道前需先删除关联任务)
-- - tasks.model_id -> models.id (RESTRICT: 删除模型前需先删除关联任务)
-- - alerts.task_id -> tasks.id (CASCADE: 删除任务时自动删除关联告警)
--
-- 索引说明：
-- - 所有外键字段都创建了索引以提高查询性能
-- - 常用查询字段（status, created_at等）创建了索引
--
-- 字符集说明：
-- - 使用 utf8mb4 字符集以支持完整的UTF-8字符（包括emoji）
-- ============================================
