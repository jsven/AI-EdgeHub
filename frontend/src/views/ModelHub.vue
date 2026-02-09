<template>
  <div class="model-hub">
    <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
      <h2>模型中心</h2>
      <el-button type="primary" @click="showUploadDialog = true">
        <el-icon><Upload /></el-icon>
        上传模型
      </el-button>
    </div>
    
    <!-- 模型列表 -->
    <el-row :gutter="20">
      <el-col :span="6" v-for="model in models" :key="model.id">
        <el-card class="model-card">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>{{ model.name }}</span>
              <el-tag size="small">{{ model.format }}</el-tag>
            </div>
          </template>
          <div>
            <p><strong>输入尺寸:</strong> {{ model.input_size || '未分析' }}</p>
            <p><strong>标签:</strong> {{ model.labels || '未分析' }}</p>
            <p><strong>创建时间:</strong> {{ formatTime(model.created_at) }}</p>
          </div>
          <template #footer>
            <div style="display: flex; gap: 10px;">
              <el-button size="small" @click="analyzeModel(model.id)">分析</el-button>
              <el-button size="small" type="danger" @click="deleteModel(model.id)">删除</el-button>
            </div>
          </template>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 上传对话框 -->
    <el-dialog v-model="showUploadDialog" title="上传模型" width="500px">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :on-change="handleFileChange"
        drag
        :limit="1"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将模型文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 ONNX、OpenVINO (.xml/.bin)、PaddlePaddle (.pdmodel) 格式
          </div>
        </template>
      </el-upload>
      
      <el-form :model="modelForm" label-width="100px" style="margin-top: 20px;">
        <el-form-item label="模型名称">
          <el-input v-model="modelForm.name" />
        </el-form-item>
        <el-form-item label="模型格式">
          <el-select v-model="modelForm.format" style="width: 100%">
            <el-option label="ONNX" value="ONNX" />
            <el-option label="OpenVINO" value="OpenVINO" />
            <el-option label="PaddlePaddle" value="PaddlePaddle" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="modelForm.description" type="textarea" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="uploadModel">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, UploadFilled } from '@element-plus/icons-vue'
import api from '@/api'
import dayjs from 'dayjs'

const models = ref([])
const showUploadDialog = ref(false)
const uploadRef = ref(null)
const modelForm = ref({
  name: '',
  format: 'ONNX',
  description: ''
})
const selectedFile = ref(null)

const loadModels = async () => {
  try {
    models.value = await api.models.list()
  } catch (error) {
    ElMessage.error('加载模型列表失败')
  }
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
  if (!modelForm.value.name) {
    modelForm.value.name = file.name.split('.')[0]
  }
}

const uploadModel = async () => {
  if (!selectedFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('name', modelForm.value.name)
    formData.append('format', modelForm.value.format)
    if (modelForm.value.description) {
      formData.append('description', modelForm.value.description)
    }
    
    await api.models.upload(formData)
    ElMessage.success('上传成功')
    showUploadDialog.value = false
    resetForm()
    loadModels()
  } catch (error) {
    ElMessage.error('上传失败')
  }
}

const analyzeModel = async (id) => {
  try {
    const result = await api.models.analyze(id)
    ElMessage.success('分析成功')
    loadModels()
  } catch (error) {
    ElMessage.error('分析失败')
  }
}

const deleteModel = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个模型吗？', '提示', {
      type: 'warning'
    })
    await api.models.delete(id)
    ElMessage.success('删除成功')
    loadModels()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

const resetForm = () => {
  modelForm.value = {
    name: '',
    format: 'ONNX',
    description: ''
  }
  selectedFile.value = null
  uploadRef.value?.clearFiles()
}

onMounted(() => {
  loadModels()
})
</script>

<style scoped>
.model-hub {
  height: 100%;
}

.model-card {
  margin-bottom: 20px;
}
</style>
