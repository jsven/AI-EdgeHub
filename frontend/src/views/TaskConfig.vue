<template>
  <div class="task-config">
    <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
      <h2>任务配置</h2>
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>
        创建任务
      </el-button>
    </div>
    
    <!-- 任务列表 -->
    <div class="page-card">
      <el-table :data="tasks" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="任务名称" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'running' ? 'success' : 'info'">
              {{ row.status === 'running' ? '运行中' : '已停止' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300">
          <template #default="{ row }">
            <el-button size="small" @click="editTask(row)">编辑</el-button>
            <el-button 
              size="small" 
              :type="row.status === 'running' ? 'warning' : 'success'"
              @click="toggleTask(row)"
            >
              {{ row.status === 'running' ? '停止' : '启动' }}
            </el-button>
            <el-button size="small" @click="cloneTask(row)">克隆</el-button>
            <el-button size="small" type="danger" @click="deleteTask(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingTask ? '编辑任务' : '创建任务'"
      width="800px"
    >
      <el-steps :active="currentStep" finish-status="success" style="margin-bottom: 20px;">
        <el-step title="选择资源" />
        <el-step title="配置ROI" />
        <el-step title="设置规则" />
      </el-steps>
      
      <!-- Step 1: 选择资源 -->
      <div v-if="currentStep === 0">
        <el-form :model="taskForm" label-width="100px">
          <el-form-item label="任务名称">
            <el-input v-model="taskForm.name" />
          </el-form-item>
          <el-form-item label="选择通道">
            <el-select v-model="taskForm.channel_id" style="width: 100%">
              <el-option
                v-for="channel in channels"
                :key="channel.id"
                :label="channel.name"
                :value="channel.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="选择模型">
            <el-select v-model="taskForm.model_id" style="width: 100%">
              <el-option
                v-for="model in models"
                :key="model.id"
                :label="model.name"
                :value="model.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="taskForm.description" type="textarea" />
          </el-form-item>
        </el-form>
      </div>
      
      <!-- Step 2: 配置ROI -->
      <div v-if="currentStep === 1">
        <el-form-item label="视频预览">
          <VideoPlayer 
            v-if="taskForm.channel_id"
            :stream-id="taskForm.channel_id"
            :show-roi="true"
            :rois="taskForm.roi_config || []"
          />
          <p v-else>请先选择通道</p>
        </el-form-item>
        <el-form-item label="ROI配置">
          <ROIDrawer
            v-model="taskForm.roi_config"
            :width="800"
            :height="600"
            :image-url="previewImageUrl"
          />
        </el-form-item>
      </div>
      
      <!-- Step 3: 设置规则 -->
      <div v-if="currentStep === 2">
        <el-form :model="taskForm" label-width="120px">
          <el-form-item label="目标标签">
            <el-input v-model="taskForm.rule_config.target_label" />
          </el-form-item>
          <el-form-item label="置信度阈值">
            <el-slider
              v-model="taskForm.rule_config.confidence_threshold"
              :min="0"
              :max="1"
              :step="0.01"
              show-input
            />
          </el-form-item>
          <el-form-item label="连续帧数">
            <el-input-number v-model="taskForm.rule_config.consecutive_frames" :min="1" />
          </el-form-item>
          <el-form-item label="检测频率">
            <el-input-number v-model="taskForm.rule_config.detection_frequency" :min="1" />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button v-if="currentStep > 0" @click="currentStep--">上一步</el-button>
        <el-button v-if="currentStep < 2" type="primary" @click="currentStep++">下一步</el-button>
        <el-button v-if="currentStep === 2" type="primary" @click="saveTask">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import VideoPlayer from '@/components/VideoPlayer.vue'
import ROIDrawer from '@/components/ROIDrawer.vue'
import api from '@/api'

const tasks = ref([])
const channels = ref([])
const models = ref([])
const showAddDialog = ref(false)
const editingTask = ref(null)
const currentStep = ref(0)
const taskForm = ref({
  name: '',
  channel_id: null,
  model_id: null,
  roi_config: [],
  rule_config: {
    target_label: '',
    confidence_threshold: 0.85,
    consecutive_frames: 1,
    detection_frequency: 1
  },
  output_config: null,
  description: ''
})
const previewImageUrl = ref('')

const loadTasks = async () => {
  try {
    tasks.value = await api.tasks.list()
  } catch (error) {
    ElMessage.error('加载任务列表失败')
  }
}

const loadChannels = async () => {
  try {
    channels.value = await api.channels.list()
  } catch (error) {
    ElMessage.error('加载通道列表失败')
  }
}

const loadModels = async () => {
  try {
    models.value = await api.models.list()
  } catch (error) {
    ElMessage.error('加载模型列表失败')
  }
}

const saveTask = async () => {
  try {
    if (editingTask.value) {
      await api.tasks.update(editingTask.value.id, taskForm.value)
      ElMessage.success('更新成功')
    } else {
      await api.tasks.create(taskForm.value)
      ElMessage.success('创建成功')
    }
    showAddDialog.value = false
    resetForm()
    loadTasks()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const editTask = (task) => {
  editingTask.value = task
  taskForm.value = {
    name: task.name,
    channel_id: task.channel_id,
    model_id: task.model_id,
    roi_config: task.roi_config ? JSON.parse(task.roi_config) : [],
    rule_config: task.rule_config ? JSON.parse(task.rule_config) : {
      target_label: '',
      confidence_threshold: 0.85,
      consecutive_frames: 1,
      detection_frequency: 1
    },
    output_config: task.output_config ? JSON.parse(task.output_config) : null,
    description: task.description || ''
  }
  currentStep.value = 0
  showAddDialog.value = true
}

const toggleTask = async (task) => {
  try {
    if (task.status === 'running') {
      await api.tasks.stop(task.id)
      ElMessage.success('任务已停止')
    } else {
      await api.tasks.start(task.id)
      ElMessage.success('任务已启动')
    }
    loadTasks()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const cloneTask = async (task) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入新任务名称', '克隆任务', {
      inputValue: `${task.name}_copy`
    })
    await api.tasks.clone(task.id, value)
    ElMessage.success('克隆成功')
    loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('克隆失败')
    }
  }
}

const deleteTask = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个任务吗？', '提示', {
      type: 'warning'
    })
    await api.tasks.delete(id)
    ElMessage.success('删除成功')
    loadTasks()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const resetForm = () => {
  editingTask.value = null
  currentStep.value = 0
  taskForm.value = {
    name: '',
    channel_id: null,
    model_id: null,
    roi_config: [],
    rule_config: {
      target_label: '',
      confidence_threshold: 0.85,
      consecutive_frames: 1,
      detection_frequency: 1
    },
    output_config: null,
    description: ''
  }
}

onMounted(() => {
  loadTasks()
  loadChannels()
  loadModels()
})
</script>

<style scoped>
.task-config {
  height: 100%;
}
</style>
