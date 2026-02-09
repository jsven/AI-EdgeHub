import { io } from 'socket.io-client'

let socket = null

export function connectWebSocket(url = 'http://localhost:8000') {
  if (socket && socket.connected) {
    return socket
  }
  
  socket = io(url, {
    transports: ['websocket'],
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: 5
  })
  
  socket.on('connect', () => {
    console.log('WebSocket连接成功')
  })
  
  socket.on('disconnect', () => {
    console.log('WebSocket连接断开')
  })
  
  socket.on('error', (error) => {
    console.error('WebSocket错误:', error)
  })
  
  return socket
}

export function disconnectWebSocket() {
  if (socket) {
    socket.disconnect()
    socket = null
  }
}

export function getSocket() {
  return socket
}
