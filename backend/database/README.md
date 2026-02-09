# 数据库表结构文件说明

本目录包含AI-EdgeHub系统的数据库表结构SQL文件。

## 文件说明

### 1. schema.sql
**SQLite数据库表结构**
- 适用于SQLite数据库（系统默认）
- 文件位置：`backend/database/schema.sql`
- 使用方法：
  ```bash
  sqlite3 ai_edgehub.db < database/schema.sql
  ```

### 2. schema_mysql.sql
**MySQL/MariaDB数据库表结构**
- 适用于MySQL 5.7+ 或 MariaDB 10.3+
- 文件位置：`backend/database/schema_mysql.sql`
- 使用方法：
  ```bash
  mysql -u root -p ai_edgehub < database/schema_mysql.sql
  ```

### 3. schema_postgresql.sql
**PostgreSQL数据库表结构**
- 适用于PostgreSQL 12+
- 文件位置：`backend/database/schema_postgresql.sql`
- 使用方法：
  ```bash
  psql -U postgres -d ai_edgehub -f database/schema_postgresql.sql
  ```

## 表结构说明

### 1. channels（通道表）
存储视频流通道配置信息。

**字段说明**：
- `id`: 通道ID（主键）
- `name`: 通道名称
- `url`: 视频流地址
- `protocol`: 协议类型（RTSP/RTMP/ONVIF/USB/FILE）
- `status`: 状态（online/offline/error）
- `description`: 描述
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 2. models（模型表）
存储AI模型文件信息。

**字段说明**：
- `id`: 模型ID（主键）
- `name`: 模型名称
- `file_path`: 模型文件路径
- `format`: 模型格式（ONNX/OpenVINO/PaddlePaddle）
- `input_size`: 输入尺寸
- `labels`: 标签列表（JSON格式）
- `description`: 描述
- `created_at`: 创建时间

### 3. tasks（任务表）
存储AI任务配置信息。

**字段说明**：
- `id`: 任务ID（主键）
- `name`: 任务名称
- `channel_id`: 关联通道ID（外键）
- `model_id`: 关联模型ID（外键）
- `roi_config`: ROI区域配置（JSON格式）
- `rule_config`: 规则配置（JSON格式）
- `output_config`: 输出配置（JSON格式）
- `status`: 状态（running/stopped/paused）
- `description`: 描述
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 4. alerts（告警表）
存储告警记录信息。

**字段说明**：
- `id`: 告警ID（主键）
- `task_id`: 关联任务ID（外键）
- `alert_type`: 告警类型
- `content`: 告警内容
- `confidence`: 置信度
- `image_path`: 告警图片路径
- `created_at`: 创建时间

## 表关系图

```
channels (通道)
    │
    │ 1:N
    │
tasks (任务) ──── N:1 ──── models (模型)
    │
    │ 1:N
    │
alerts (告警)
```

## 外键约束

1. **tasks.channel_id → channels.id**
   - 约束类型：RESTRICT
   - 说明：删除通道前需先删除关联的任务

2. **tasks.model_id → models.id**
   - 约束类型：RESTRICT
   - 说明：删除模型前需先删除关联的任务

3. **alerts.task_id → tasks.id**
   - 约束类型：CASCADE
   - 说明：删除任务时自动删除关联的告警记录

## 索引说明

为了提高查询性能，以下字段创建了索引：

- `channels`: status, protocol, created_at
- `models`: format, created_at
- `tasks`: channel_id, model_id, status, created_at
- `alerts`: task_id, alert_type, created_at, confidence

## 使用示例

### SQLite（默认）

```bash
# 创建数据库并导入表结构
sqlite3 ai_edgehub.db < database/schema.sql

# 或者使用Python脚本
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
```

### MySQL

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE ai_edgehub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 导入表结构
mysql -u root -p ai_edgehub < database/schema_mysql.sql
```

### PostgreSQL

```bash
# 创建数据库
createdb -U postgres ai_edgehub

# 导入表结构
psql -U postgres -d ai_edgehub -f database/schema_postgresql.sql
```

## 注意事项

1. **SQLite限制**：
   - SQLite不支持外键约束的强制执行（需要启用PRAGMA foreign_keys）
   - SQLite的TEXT类型可以存储任意长度的字符串

2. **MySQL注意事项**：
   - 使用InnoDB引擎以支持外键约束
   - 使用utf8mb4字符集以支持完整的UTF-8字符

3. **PostgreSQL注意事项**：
   - 使用SERIAL类型作为自增主键
   - 使用TIMESTAMP WITH TIME ZONE支持时区

4. **数据迁移**：
   - 从SQLite迁移到MySQL/PostgreSQL时，需要注意数据类型差异
   - 建议使用数据库迁移工具（如Alembic）进行版本管理

## 版本历史

- **v1.0.0** (2024-01-01): 初始版本，包含4个核心表

## 相关文档

- [技术架构设计](../docs/技术架构设计.md)
- [功能详细说明](../docs/功能详细说明.md)
- [操作手册](../docs/操作手册.md)
