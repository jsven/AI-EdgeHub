-- ============================================
-- AI-EdgeHub 数据库表结构定义
-- 数据库类型: PostgreSQL 12+
-- 版本: 1.0.0
-- 创建日期: 2024-01-01
-- ============================================

-- 创建数据库（如果不存在）
-- CREATE DATABASE ai_edgehub;
-- \c ai_edgehub;

-- 启用UUID扩展（如果需要）
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. 通道表 (channels)
-- 存储视频流通道配置信息
-- ============================================
CREATE TABLE IF NOT EXISTS channels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    url TEXT NOT NULL,
    protocol VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'offline',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE channels IS '视频通道表';
COMMENT ON COLUMN channels.id IS '通道ID';
COMMENT ON COLUMN channels.name IS '通道名称';
COMMENT ON COLUMN channels.url IS '视频流地址';
COMMENT ON COLUMN channels.protocol IS '协议类型: RTSP/RTMP/ONVIF/USB/FILE';
COMMENT ON COLUMN channels.status IS '状态: online/offline/error';
COMMENT ON COLUMN channels.description IS '描述';
COMMENT ON COLUMN channels.created_at IS '创建时间';
COMMENT ON COLUMN channels.updated_at IS '更新时间';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_channels_status ON channels(status);
CREATE INDEX IF NOT EXISTS idx_channels_protocol ON channels(protocol);
CREATE INDEX IF NOT EXISTS idx_channels_created_at ON channels(created_at);

-- ============================================
-- 2. 模型表 (models)
-- 存储AI模型文件信息
-- ============================================
CREATE TABLE IF NOT EXISTS models (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    file_path TEXT NOT NULL,
    format VARCHAR(20) NOT NULL,
    input_size VARCHAR(50),
    labels TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE models IS 'AI模型表';
COMMENT ON COLUMN models.id IS '模型ID';
COMMENT ON COLUMN models.name IS '模型名称';
COMMENT ON COLUMN models.file_path IS '模型文件路径';
COMMENT ON COLUMN models.format IS '模型格式: ONNX/OpenVINO/PaddlePaddle';
COMMENT ON COLUMN models.input_size IS '输入尺寸，如: 640,640';
COMMENT ON COLUMN models.labels IS '标签列表，JSON格式';
COMMENT ON COLUMN models.description IS '描述';
COMMENT ON COLUMN models.created_at IS '创建时间';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_models_format ON models(format);
CREATE INDEX IF NOT EXISTS idx_models_created_at ON models(created_at);

-- ============================================
-- 3. 任务表 (tasks)
-- 存储AI任务配置信息
-- ============================================
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    channel_id INTEGER NOT NULL,
    model_id INTEGER NOT NULL,
    roi_config TEXT,
    rule_config TEXT,
    output_config TEXT,
    status VARCHAR(20) DEFAULT 'stopped',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_tasks_channel FOREIGN KEY (channel_id) REFERENCES channels(id) ON DELETE RESTRICT,
    CONSTRAINT fk_tasks_model FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE RESTRICT
);

COMMENT ON TABLE tasks IS 'AI任务表';
COMMENT ON COLUMN tasks.id IS '任务ID';
COMMENT ON COLUMN tasks.name IS '任务名称';
COMMENT ON COLUMN tasks.channel_id IS '关联通道ID';
COMMENT ON COLUMN tasks.model_id IS '关联模型ID';
COMMENT ON COLUMN tasks.roi_config IS 'ROI区域配置，JSON格式';
COMMENT ON COLUMN tasks.rule_config IS '规则配置，JSON格式';
COMMENT ON COLUMN tasks.output_config IS '输出配置，JSON格式';
COMMENT ON COLUMN tasks.status IS '状态: running/stopped/paused';
COMMENT ON COLUMN tasks.description IS '描述';
COMMENT ON COLUMN tasks.created_at IS '创建时间';
COMMENT ON COLUMN tasks.updated_at IS '更新时间';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_tasks_channel_id ON tasks(channel_id);
CREATE INDEX IF NOT EXISTS idx_tasks_model_id ON tasks(model_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);

-- ============================================
-- 4. 告警表 (alerts)
-- 存储告警记录信息
-- ============================================
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    content TEXT,
    confidence REAL,
    image_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_alerts_task FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

COMMENT ON TABLE alerts IS '告警记录表';
COMMENT ON COLUMN alerts.id IS '告警ID';
COMMENT ON COLUMN alerts.task_id IS '关联任务ID';
COMMENT ON COLUMN alerts.alert_type IS '告警类型';
COMMENT ON COLUMN alerts.content IS '告警内容';
COMMENT ON COLUMN alerts.confidence IS '置信度';
COMMENT ON COLUMN alerts.image_path IS '告警图片路径';
COMMENT ON COLUMN alerts.created_at IS '创建时间';

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_alerts_task_id ON alerts(task_id);
CREATE INDEX IF NOT EXISTS idx_alerts_alert_type ON alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at);
CREATE INDEX IF NOT EXISTS idx_alerts_confidence ON alerts(confidence);

-- ============================================
-- 触发器：自动更新 updated_at 字段
-- ============================================

-- 创建更新updated_at的函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- channels 表更新触发器
DROP TRIGGER IF EXISTS update_channels_timestamp ON channels;
CREATE TRIGGER update_channels_timestamp
    BEFORE UPDATE ON channels
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- tasks 表更新触发器
DROP TRIGGER IF EXISTS update_tasks_timestamp ON tasks;
CREATE TRIGGER update_tasks_timestamp
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

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
-- 时间戳说明：
-- - 使用 TIMESTAMP WITH TIME ZONE 类型以支持时区
-- ============================================
