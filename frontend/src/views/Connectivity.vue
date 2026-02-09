<template>
  <div class="connectivity">
    <h2 style="margin-bottom: 20px;">工业互联设置</h2>
    
    <el-tabs v-model="activeTab">
      <!-- Modbus TCP 配置 -->
      <el-tab-pane label="Modbus TCP" name="modbus">
        <div class="page-card">
          <el-form :model="modbusConfig" label-width="150px">
            <el-form-item label="PLC IP地址">
              <el-input v-model="modbusConfig.host" />
            </el-form-item>
            <el-form-item label="端口">
              <el-input-number v-model="modbusConfig.port" :min="1" :max="65535" />
            </el-form-item>
            <el-form-item label="从站ID">
              <el-input-number v-model="modbusConfig.slave_id" :min="1" :max="255" />
            </el-form-item>
            <el-form-item label="超时时间(秒)">
              <el-input-number v-model="modbusConfig.timeout" :min="1" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="testModbus">测试连接</el-button>
              <el-button @click="saveModbusConfig">保存配置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
      
      <!-- MQTT 配置 -->
      <el-tab-pane label="MQTT" name="mqtt">
        <div class="page-card">
          <el-form :model="mqttConfig" label-width="150px">
            <el-form-item label="Broker地址">
              <el-input v-model="mqttConfig.broker" />
            </el-form-item>
            <el-form-item label="端口">
              <el-input-number v-model="mqttConfig.port" :min="1" :max="65535" />
            </el-form-item>
            <el-form-item label="用户名">
              <el-input v-model="mqttConfig.username" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="mqttConfig.password" type="password" show-password />
            </el-form-item>
            <el-form-item label="主题前缀">
              <el-input v-model="mqttConfig.topic_prefix" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="testMQTT">测试连接</el-button>
              <el-button @click="saveMQTTConfig">保存配置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
      
      <!-- Webhook 配置 -->
      <el-tab-pane label="Webhook" name="webhook">
        <div class="page-card">
          <el-form :model="webhookConfig" label-width="150px">
            <el-form-item label="Webhook URL">
              <el-input v-model="webhookConfig.url" />
            </el-form-item>
            <el-form-item label="请求方法">
              <el-select v-model="webhookConfig.method" style="width: 100%">
                <el-option label="POST" value="POST" />
                <el-option label="GET" value="GET" />
              </el-select>
            </el-form-item>
            <el-form-item label="请求头(JSON)">
              <el-input v-model="webhookConfig.headers" type="textarea" />
            </el-form-item>
            <el-form-item>
              <el-button @click="saveWebhookConfig">保存配置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
      
      <!-- 模拟触发 -->
      <el-tab-pane label="模拟触发" name="simulate">
        <div class="page-card">
          <el-form label-width="150px">
            <el-form-item label="输出类型">
              <el-select v-model="simulateType" style="width: 100%">
                <el-option label="Modbus TCP" value="modbus" />
                <el-option label="MQTT" value="mqtt" />
                <el-option label="Webhook" value="webhook" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="simulateTrigger">模拟触发</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const activeTab = ref('modbus')
const modbusConfig = ref({
  host: '192.168.1.100',
  port: 502,
  slave_id: 1,
  timeout: 5
})
const mqttConfig = ref({
  broker: 'localhost',
  port: 1883,
  username: '',
  password: '',
  topic_prefix: '/ai-edgehub'
})
const webhookConfig = ref({
  url: '',
  method: 'POST',
  headers: '{}'
})
const simulateType = ref('modbus')

const loadConfig = async () => {
  try {
    const config = await api.connectivity.getConfig()
    if (config.modbus) {
      modbusConfig.value = { ...modbusConfig.value, ...config.modbus }
    }
    if (config.mqtt) {
      mqttConfig.value = { ...mqttConfig.value, ...config.mqtt }
    }
    if (config.webhook) {
      webhookConfig.value = { ...webhookConfig.value, ...config.webhook }
    }
  } catch (error) {
    console.error('加载配置失败:', error)
  }
}

const testModbus = async () => {
  try {
    const result = await api.connectivity.testModbus(modbusConfig.value)
    if (result.success) {
      ElMessage.success('Modbus连接测试成功')
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('测试失败')
  }
}

const testMQTT = async () => {
  try {
    const result = await api.connectivity.testMQTT(mqttConfig.value)
    if (result.success) {
      ElMessage.success('MQTT连接测试成功')
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('测试失败')
  }
}

const saveModbusConfig = async () => {
  try {
    await api.connectivity.updateConfig({
      modbus: modbusConfig.value
    })
    ElMessage.success('配置保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const saveMQTTConfig = async () => {
  try {
    await api.connectivity.updateConfig({
      mqtt: mqttConfig.value
    })
    ElMessage.success('配置保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const saveWebhookConfig = async () => {
  try {
    await api.connectivity.updateConfig({
      webhook: webhookConfig.value
    })
    ElMessage.success('配置保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const simulateTrigger = async () => {
  try {
    const config = simulateType.value === 'modbus' 
      ? modbusConfig.value 
      : simulateType.value === 'mqtt'
      ? mqttConfig.value
      : webhookConfig.value
    
    const result = await api.connectivity.simulateTrigger(simulateType.value, config)
    if (result.success) {
      ElMessage.success('模拟触发成功')
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('触发失败')
  }
}

onMounted(() => {
  loadConfig()
})
</script>

<style scoped>
.connectivity {
  height: 100%;
}
</style>
