<template>
  <div class="video-player">
    <div class="video-container" ref="containerRef">
      <img 
        v-if="frameUrl" 
        :src="frameUrl" 
        alt="视频流"
        class="video-frame"
      />
      <div v-else class="video-placeholder">
        <el-icon :size="48"><VideoCamera /></el-icon>
        <p>等待视频流...</p>
      </div>
      
      <!-- ROI绘制层 -->
      <canvas
        v-if="showROI"
        ref="roiCanvasRef"
        class="roi-canvas"
        :width="canvasWidth"
        :height="canvasHeight"
      ></canvas>
    </div>
    
    <div class="video-info">
      <el-tag v-if="fps > 0">FPS: {{ fps.toFixed(1) }}</el-tag>
      <el-tag :type="connected ? 'success' : 'danger'">
        {{ connected ? '已连接' : '未连接' }}
      </el-tag>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { VideoCamera } from '@element-plus/icons-vue'
import { connectWebSocket, disconnectWebSocket, getSocket } from '@/utils/websocket'

const props = defineProps({
  streamId: {
    type: Number,
    default: null
  },
  showROI: {
    type: Boolean,
    default: false
  },
  rois: {
    type: Array,
    default: () => []
  }
})

const containerRef = ref(null)
const roiCanvasRef = ref(null)
const frameUrl = ref('')
const fps = ref(0)
const connected = ref(false)
const canvasWidth = ref(800)
const canvasHeight = ref(600)
let socket = null

onMounted(() => {
  if (props.streamId) {
    startPreview()
  }
})

onUnmounted(() => {
  stopPreview()
})

watch(() => props.streamId, (newId) => {
  if (newId) {
    startPreview()
  } else {
    stopPreview()
  }
})

watch(() => props.rois, () => {
  drawROIs()
}, { deep: true })

const startPreview = () => {
  if (!props.streamId) return
  
  socket = connectWebSocket()
  
  socket.on('connect', () => {
    connected.value = true
    // 订阅视频流
    socket.emit('subscribe', { channel: `preview_${props.streamId}` })
  })
  
  socket.on('disconnect', () => {
    connected.value = false
  })
  
  socket.on('frame', (data) => {
    if (data.stream_id === props.streamId) {
      frameUrl.value = data.frame
      fps.value = data.fps || 0
      
      // 更新画布尺寸
      const img = new Image()
      img.onload = () => {
        canvasWidth.value = img.width
        canvasHeight.value = img.height
        if (roiCanvasRef.value) {
          roiCanvasRef.value.width = img.width
          roiCanvasRef.value.height = img.height
          drawROIs()
        }
      }
      img.src = data.frame
    }
  })
  
  // 使用WebSocket直接连接
  const ws = new WebSocket(`ws://localhost:8000/ws/preview/${props.streamId}`)
  
  ws.onopen = () => {
    connected.value = true
  }
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'frame') {
        frameUrl.value = data.frame
        fps.value = data.fps || 0
        
        // 更新画布尺寸
        const img = new Image()
        img.onload = () => {
          canvasWidth.value = img.width
          canvasHeight.value = img.height
          if (roiCanvasRef.value) {
            roiCanvasRef.value.width = img.width
            roiCanvasRef.value.height = img.height
            drawROIs()
          }
        }
        img.src = data.frame
      }
    } catch (e) {
      console.error('解析WebSocket消息失败:', e)
    }
  }
  
  ws.onerror = () => {
    connected.value = false
  }
  
  ws.onclose = () => {
    connected.value = false
  }
}

const stopPreview = () => {
  if (socket) {
    disconnectWebSocket()
    socket = null
  }
  frameUrl.value = ''
  fps.value = 0
  connected.value = false
}

const drawROIs = () => {
  if (!roiCanvasRef.value || !props.showROI || !props.rois.length) {
    return
  }
  
  const ctx = roiCanvasRef.value.getContext('2d')
  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)
  
  props.rois.forEach(roi => {
    if (roi.type === 'polygon' && roi.points.length >= 3) {
      ctx.strokeStyle = '#409eff'
      ctx.fillStyle = 'rgba(64, 158, 255, 0.3)'
      ctx.lineWidth = 2
      
      ctx.beginPath()
      ctx.moveTo(roi.points[0].x, roi.points[0].y)
      for (let i = 1; i < roi.points.length; i++) {
        ctx.lineTo(roi.points[i].x, roi.points[i].y)
      }
      ctx.closePath()
      ctx.fill()
      ctx.stroke()
    } else if (roi.type === 'rectangle' && roi.points.length >= 2) {
      const [p1, p2] = roi.points
      const x = Math.min(p1.x, p2.x)
      const y = Math.min(p1.y, p2.y)
      const w = Math.abs(p2.x - p1.x)
      const h = Math.abs(p2.y - p1.y)
      
      ctx.strokeStyle = '#409eff'
      ctx.fillStyle = 'rgba(64, 158, 255, 0.3)'
      ctx.lineWidth = 2
      ctx.fillRect(x, y, w, h)
      ctx.strokeRect(x, y, w, h)
    } else if (roi.type === 'line' && roi.points.length >= 2) {
      const [p1, p2] = roi.points
      ctx.strokeStyle = '#f56c6c'
      ctx.lineWidth = 3
      ctx.beginPath()
      ctx.moveTo(p1.x, p1.y)
      ctx.lineTo(p2.x, p2.y)
      ctx.stroke()
    }
  })
}
</script>

<style scoped>
.video-player {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.video-container {
  position: relative;
  width: 100%;
  background: #000;
  border-radius: 4px;
  overflow: hidden;
}

.video-frame {
  width: 100%;
  height: auto;
  display: block;
}

.video-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #909399;
}

.roi-canvas {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}

.video-info {
  display: flex;
  gap: 10px;
}
</style>
