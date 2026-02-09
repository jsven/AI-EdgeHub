<template>
  <div class="roi-drawer">
    <div class="toolbar">
      <el-button-group>
        <el-button 
          :type="drawMode === 'polygon' ? 'primary' : ''"
          @click="setDrawMode('polygon')"
        >
          <el-icon><EditPen /></el-icon>
          多边形
        </el-button>
        <el-button 
          :type="drawMode === 'rectangle' ? 'primary' : ''"
          @click="setDrawMode('rectangle')"
        >
          <el-icon><Crop /></el-icon>
          矩形
        </el-button>
        <el-button 
          :type="drawMode === 'line' ? 'primary' : ''"
          @click="setDrawMode('line')"
        >
          <el-icon><Minus /></el-icon>
          绊线
        </el-button>
        <el-button @click="clearCurrent">
          <el-icon><Delete /></el-icon>
          清除当前
        </el-button>
        <el-button @click="clearAll">
          <el-icon><DeleteFilled /></el-icon>
          清除全部
        </el-button>
      </el-button-group>
    </div>
    
    <div class="canvas-container">
      <canvas
        ref="canvasRef"
        :width="canvasWidth"
        :height="canvasHeight"
        @mousedown="onMouseDown"
        @mousemove="onMouseMove"
        @mouseup="onMouseUp"
        @click="onClick"
      ></canvas>
    </div>
    
    <div class="roi-list">
      <h4>ROI区域列表</h4>
      <el-table :data="roiList" style="width: 100%">
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column prop="points" label="坐标点">
          <template #default="{ row }">
            {{ formatPoints(row.points) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row, $index }">
            <el-button size="small" type="danger" @click="removeROI($index)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { EditPen, Crop, Minus, Delete, DeleteFilled } from '@element-plus/icons-vue'

const props = defineProps({
  width: {
    type: Number,
    default: 800
  },
  height: {
    type: Number,
    default: 600
  },
  imageUrl: {
    type: String,
    default: ''
  },
  modelValue: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

const canvasRef = ref(null)
const canvasWidth = ref(props.width)
const canvasHeight = ref(props.height)
const drawMode = ref('polygon') // polygon, rectangle, line
const roiList = ref([...props.modelValue])
const isDrawing = ref(false)
const currentPoints = ref([])
const ctx = ref(null)
const image = ref(null)

onMounted(() => {
  if (canvasRef.value) {
    ctx.value = canvasRef.value.getContext('2d')
    if (props.imageUrl) {
      loadImage()
    }
    drawAllROIs()
  }
})

watch(() => props.modelValue, (newVal) => {
  roiList.value = [...newVal]
  drawAllROIs()
})

watch(() => props.imageUrl, () => {
  if (props.imageUrl) {
    loadImage()
  }
})

const loadImage = () => {
  const img = new Image()
  img.crossOrigin = 'anonymous'
  img.onload = () => {
    image.value = img
    canvasWidth.value = img.width
    canvasHeight.value = img.height
    if (canvasRef.value) {
      canvasRef.value.width = img.width
      canvasRef.value.height = img.height
      drawAllROIs()
    }
  }
  img.src = props.imageUrl
}

const setDrawMode = (mode) => {
  drawMode.value = mode
  currentPoints.value = []
  isDrawing.value = false
  drawAllROIs()
}

const getMousePos = (e) => {
  const rect = canvasRef.value.getBoundingClientRect()
  return {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  }
}

const onMouseDown = (e) => {
  if (drawMode.value === 'rectangle' || drawMode.value === 'line') {
    isDrawing.value = true
    const pos = getMousePos(e)
    currentPoints.value = [pos]
  }
}

const onMouseMove = (e) => {
  if (isDrawing.value && currentPoints.value.length > 0) {
    drawAllROIs()
    const pos = getMousePos(e)
    if (drawMode.value === 'rectangle') {
      drawRectangle(currentPoints.value[0], pos)
    } else if (drawMode.value === 'line') {
      drawLine(currentPoints.value[0], pos)
    }
  }
}

const onMouseUp = (e) => {
  if (isDrawing.value) {
    const pos = getMousePos(e)
    if (drawMode.value === 'rectangle' || drawMode.value === 'line') {
      currentPoints.value.push(pos)
      finishDrawing()
    }
    isDrawing.value = false
  }
}

const onClick = (e) => {
  if (drawMode.value === 'polygon') {
    const pos = getMousePos(e)
    currentPoints.value.push(pos)
    drawAllROIs()
    drawPolygon(currentPoints.value)
  }
}

const finishDrawing = () => {
  if (currentPoints.value.length >= 2) {
    const roi = {
      type: drawMode.value,
      points: [...currentPoints.value]
    }
    roiList.value.push(roi)
    currentPoints.value = []
    updateModelValue()
    drawAllROIs()
  }
}

const drawPolygon = (points) => {
  if (points.length < 2) return
  
  ctx.value.strokeStyle = '#409eff'
  ctx.value.fillStyle = 'rgba(64, 158, 255, 0.3)'
  ctx.value.lineWidth = 2
  
  ctx.value.beginPath()
  ctx.value.moveTo(points[0].x, points[0].y)
  for (let i = 1; i < points.length; i++) {
    ctx.value.lineTo(points[i].x, points[i].y)
  }
  ctx.value.closePath()
  ctx.value.fill()
  ctx.value.stroke()
  
  // 绘制点
  points.forEach((point, index) => {
    ctx.value.fillStyle = '#409eff'
    ctx.value.beginPath()
    ctx.value.arc(point.x, point.y, 4, 0, Math.PI * 2)
    ctx.value.fill()
    
    ctx.value.fillStyle = '#fff'
    ctx.value.font = '12px Arial'
    ctx.value.fillText(index + 1, point.x - 4, point.y - 8)
  })
}

const drawRectangle = (start, end) => {
  ctx.value.strokeStyle = '#409eff'
  ctx.value.fillStyle = 'rgba(64, 158, 255, 0.3)'
  ctx.value.lineWidth = 2
  
  const x = Math.min(start.x, end.x)
  const y = Math.min(start.y, end.y)
  const w = Math.abs(end.x - start.x)
  const h = Math.abs(end.y - start.y)
  
  ctx.value.fillRect(x, y, w, h)
  ctx.value.strokeRect(x, y, w, h)
}

const drawLine = (start, end) => {
  ctx.value.strokeStyle = '#f56c6c'
  ctx.value.lineWidth = 3
  
  ctx.value.beginPath()
  ctx.value.moveTo(start.x, start.y)
  ctx.value.lineTo(end.x, end.y)
  ctx.value.stroke()
  
  // 绘制端点
  [start, end].forEach(point => {
    ctx.value.fillStyle = '#f56c6c'
    ctx.value.beginPath()
    ctx.value.arc(point.x, point.y, 5, 0, Math.PI * 2)
    ctx.value.fill()
  })
}

const drawAllROIs = () => {
  if (!ctx.value) return
  
  // 清空画布
  ctx.value.clearRect(0, 0, canvasWidth.value, canvasHeight.value)
  
  // 绘制背景图片
  if (image.value) {
    ctx.value.drawImage(image.value, 0, 0)
  }
  
  // 绘制所有ROI
  roiList.value.forEach(roi => {
    if (roi.type === 'polygon') {
      drawPolygon(roi.points)
    } else if (roi.type === 'rectangle') {
      if (roi.points.length >= 2) {
        drawRectangle(roi.points[0], roi.points[1])
      }
    } else if (roi.type === 'line') {
      if (roi.points.length >= 2) {
        drawLine(roi.points[0], roi.points[1])
      }
    }
  })
  
  // 绘制当前正在绘制的ROI
  if (currentPoints.value.length > 0) {
    if (drawMode.value === 'polygon') {
      drawPolygon(currentPoints.value)
    }
  }
}

const clearCurrent = () => {
  currentPoints.value = []
  drawAllROIs()
}

const clearAll = () => {
  roiList.value = []
  currentPoints.value = []
  updateModelValue()
  drawAllROIs()
}

const removeROI = (index) => {
  roiList.value.splice(index, 1)
  updateModelValue()
  drawAllROIs()
}

const formatPoints = (points) => {
  return points.map(p => `(${p.x.toFixed(0)}, ${p.y.toFixed(0)})`).join(', ')
}

const updateModelValue = () => {
  emit('update:modelValue', roiList.value)
}

// 完成多边形绘制（双击或按Enter）
const completePolygon = () => {
  if (drawMode.value === 'polygon' && currentPoints.value.length >= 3) {
    finishDrawing()
  }
}

defineExpose({
  completePolygon,
  getROIs: () => roiList.value
})
</script>

<style scoped>
.roi-drawer {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.toolbar {
  display: flex;
  gap: 10px;
}

.canvas-container {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  background: #f5f7fa;
}

canvas {
  display: block;
  cursor: crosshair;
}

.roi-list {
  margin-top: 20px;
}
</style>
