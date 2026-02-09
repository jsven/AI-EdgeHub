import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/views/Layout.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘', icon: 'DataBoard' }
      },
      {
        path: 'channels',
        name: 'ChannelManagement',
        component: () => import('@/views/ChannelManagement.vue'),
        meta: { title: '通道管理', icon: 'VideoCamera' }
      },
      {
        path: 'models',
        name: 'ModelHub',
        component: () => import('@/views/ModelHub.vue'),
        meta: { title: '模型中心', icon: 'Box' }
      },
      {
        path: 'tasks',
        name: 'TaskConfig',
        component: () => import('@/views/TaskConfig.vue'),
        meta: { title: '任务配置', icon: 'Setting' }
      },
      {
        path: 'connectivity',
        name: 'Connectivity',
        component: () => import('@/views/Connectivity.vue'),
        meta: { title: '工业互联', icon: 'Connection' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
