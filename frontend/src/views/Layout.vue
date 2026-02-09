<template>
  <div class="app-container">
    <header class="app-header">
      <div class="header-left">
        <h1 style="margin: 0; font-size: 20px; color: #303133;">
          <el-icon><Box /></el-icon>
          AI-EdgeHub
        </h1>
      </div>
      <div class="header-right">
        <el-badge :value="12" class="item">
          <el-icon :size="20"><Bell /></el-icon>
        </el-badge>
      </div>
    </header>
    
    <div class="app-main">
      <aside class="app-sidebar">
        <el-menu
          :default-active="activeMenu"
          router
          background-color="#fff"
          text-color="#303133"
          active-text-color="#409eff"
        >
          <el-menu-item index="/dashboard">
            <el-icon><DataBoard /></el-icon>
            <span>仪表盘</span>
          </el-menu-item>
          <el-menu-item index="/channels">
            <el-icon><VideoCamera /></el-icon>
            <span>通道管理</span>
          </el-menu-item>
          <el-menu-item index="/models">
            <el-icon><Box /></el-icon>
            <span>模型中心</span>
          </el-menu-item>
          <el-menu-item index="/tasks">
            <el-icon><Setting /></el-icon>
            <span>任务配置</span>
          </el-menu-item>
          <el-menu-item index="/connectivity">
            <el-icon><Connection /></el-icon>
            <span>工业互联</span>
          </el-menu-item>
        </el-menu>
      </aside>
      
      <main class="app-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { DataBoard, VideoCamera, Box, Setting, Connection, Bell } from '@element-plus/icons-vue'

const route = useRoute()

const activeMenu = computed(() => {
  return route.path
})
</script>

<style scoped>
.header-left {
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.item {
  cursor: pointer;
}
</style>
