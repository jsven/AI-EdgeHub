<template>
  <div class="channel-management">
    <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
      <h2>通道管理</h2>
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>
        新增通道
      </el-button>
    </div>
    
    <!-- 通道列表 -->
    <div class="page-card">
      <el-table :data="channels" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="通道名称" />
        <el-table-column prop="protocol" label="协议类型" />
        <el-table-column prop="url" label="视频流地址" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'online' ? 'success' : 'danger'">
              {{ row.status === 'online' ? '在线' : '离线' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="previewChannel(row)">预览</el-button>
            <el-button size="small" @click="editChannel(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteChannel(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="editingChannel ? '编辑通道' : '新增通道'"
      width="600px"
    >
      <el-form :model="channelForm" label-width="100px">
        <el-form-item label="通道名称">
          <el-input v-model="channelForm.name" />
        </el-form-item>
        <el-form-item label="协议类型">
          <el-select v-model="channelForm.protocol" style="width: 100%">
            <el-option label="RTSP" value="RTSP" />
            <el-option label="RTMP" value="RTMP" />
            <el-option label="ONVIF" value="ONVIF" />
            <el-option label="USB" value="USB" />
            <el-option label="本地文件" value="FILE" />
          </el-select>
        </el-form-item>
        <el-form-item label="视频流地址">
          <el-input v-model="channelForm.url" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="channelForm.description" type="textarea" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="saveChannel">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/api'

const channels = ref([])
const showAddDialog = ref(false)
const editingChannel = ref(null)
const channelForm = ref({
  name: '',
  protocol: 'RTSP',
  url: '',
  description: ''
})

const loadChannels = async () => {
  try {
    channels.value = await api.channels.list()
  } catch (error) {
    ElMessage.error('加载通道列表失败')
  }
}

const saveChannel = async () => {
  try {
    if (editingChannel.value) {
      await api.channels.update(editingChannel.value.id, channelForm.value)
      ElMessage.success('更新成功')
    } else {
      await api.channels.create(channelForm.value)
      ElMessage.success('创建成功')
    }
    showAddDialog.value = false
    resetForm()
    loadChannels()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const editChannel = (channel) => {
  editingChannel.value = channel
  channelForm.value = {
    name: channel.name,
    protocol: channel.protocol,
    url: channel.url,
    description: channel.description || ''
  }
  showAddDialog.value = true
}

const deleteChannel = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个通道吗？', '提示', {
      type: 'warning'
    })
    await api.channels.delete(id)
    ElMessage.success('删除成功')
    loadChannels()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const previewChannel = async (channel) => {
  try {
    const result = await api.channels.preview({
      url: channel.url,
      protocol: channel.protocol
    })
    if (result.success) {
      ElMessage.success('预览成功')
      // TODO: 打开预览窗口
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('预览失败')
  }
}

const resetForm = () => {
  editingChannel.value = null
  channelForm.value = {
    name: '',
    protocol: 'RTSP',
    url: '',
    description: ''
  }
}

onMounted(() => {
  loadChannels()
})
</script>

<style scoped>
.channel-management {
  height: 100%;
}
</style>
