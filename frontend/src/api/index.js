import request from '@/utils/request'

export default {
  // 通道管理
  channels: {
    list: () => request.get('/channels'),
    get: (id) => request.get(`/channels/${id}`),
    create: (data) => request.post('/channels', data),
    update: (id, data) => request.put(`/channels/${id}`, data),
    delete: (id) => request.delete(`/channels/${id}`),
    preview: (data) => request.post('/channels/preview', data),
    batchCheck: () => request.post('/channels/batch-check')
  },
  
  // 模型管理
  models: {
    list: () => request.get('/models'),
    get: (id) => request.get(`/models/${id}`),
    upload: (formData) => request.post('/models', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
    delete: (id) => request.delete(`/models/${id}`),
    analyze: (id) => request.post(`/models/${id}/analyze`)
  },
  
  // 任务管理
  tasks: {
    list: () => request.get('/tasks'),
    get: (id) => request.get(`/tasks/${id}`),
    create: (data) => request.post('/tasks', data),
    update: (id, data) => request.put(`/tasks/${id}`, data),
    delete: (id) => request.delete(`/tasks/${id}`),
    start: (id) => request.post(`/tasks/${id}/start`),
    stop: (id) => request.post(`/tasks/${id}/stop`),
    clone: (id, newName) => request.post(`/tasks/${id}/clone?new_name=${newName}`)
  },
  
  // 仪表盘
  dashboard: {
    get: () => request.get('/dashboard'),
    getStats: () => request.get('/dashboard/stats'),
    getPerformance: (hours) => request.get(`/dashboard/performance?hours=${hours}`)
  },
  
  // 工业互联
  connectivity: {
    getConfig: () => request.get('/connectivity/config'),
    updateConfig: (data) => request.put('/connectivity/config', data),
    testModbus: (data) => request.post('/connectivity/test/modbus', data),
    testMQTT: (data) => request.post('/connectivity/test/mqtt', data),
    simulateTrigger: (outputType, config) => request.post('/connectivity/test/simulate-trigger', {
      output_type: outputType,
      config
    })
  }
}
