<template>
  <div class="dashboard">
    <h2 style="margin-bottom: 20px;">仪表盘</h2>
    
    <!-- 系统统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="page-card stats-card">
          <div class="stats-label">CPU使用率</div>
          <div class="stats-value">{{ systemStats.cpu_usage?.toFixed(1) || 0 }}%</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="page-card stats-card">
          <div class="stats-label">内存使用率</div>
          <div class="stats-value">{{ systemStats.memory_usage?.toFixed(1) || 0 }}%</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="page-card stats-card">
          <div class="stats-label">活跃通道</div>
          <div class="stats-value">{{ systemStats.active_channels || 0 }}/{{ systemStats.total_channels || 0 }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="page-card stats-card">
          <div class="stats-label">运行任务</div>
          <div class="stats-value">{{ systemStats.running_tasks || 0 }}/{{ systemStats.total_tasks || 0 }}</div>
        </div>
      </el-col>
    </el-row>
    
    <!-- 通道状态 -->
    <div class="page-card">
      <h3 style="margin-bottom: 15px;">通道状态</h3>
      <el-table :data="channelStats" style="width: 100%">
        <el-table-column prop="channel_name" label="通道名称" />
        <el-table-column prop="fps" label="帧率(FPS)" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'online' ? 'success' : 'danger'">
              {{ row.status === 'online' ? '在线' : '离线' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="inference_latency" label="推理延迟(ms)">
          <template #default="{ row }">
            {{ row.inference_latency ? row.inference_latency.toFixed(2) : '-' }}
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 最近告警 -->
    <div class="page-card">
      <h3 style="margin-bottom: 15px;">最近告警</h3>
      <el-timeline>
        <el-timeline-item
          v-for="alert in recentAlerts"
          :key="alert.id"
          :timestamp="formatTime(alert.created_at)"
          placement="top"
        >
          <el-card>
            <h4>{{ alert.task_name }} - {{ alert.alert_type }}</h4>
            <p>{{ alert.content }}</p>
            <p v-if="alert.confidence">置信度: {{ (alert.confidence * 100).toFixed(2) }}%</p>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import dayjs from 'dayjs'

const systemStats = ref({
  cpu_usage: 0,
  memory_usage: 0,
  total_channels: 0,
  active_channels: 0,
  total_tasks: 0,
  running_tasks: 0
})

const channelStats = ref([])
const recentAlerts = ref([])

const loadDashboard = async () => {
  try {
    const data = await api.dashboard.get()
    systemStats.value = data.system_stats
    channelStats.value = data.channel_stats
    recentAlerts.value = data.recent_alerts
  } catch (error) {
    console.error('加载仪表盘数据失败:', error)
  }
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

onMounted(() => {
  loadDashboard()
  // 每5秒刷新一次
  setInterval(loadDashboard, 5000)
})
</script>

<style scoped>
.dashboard {
  height: 100%;
}
</style>
