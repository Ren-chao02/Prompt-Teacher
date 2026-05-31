import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/request'

export const useNotificationsStore = defineStore('notifications', () => {
  // 状态
  const notifications = ref([])
  const unreadCount = ref(0)
  const unreadBreakdown = ref({})
  const loading = ref(false)
  const wsConnected = ref(false)
  
  let websocket = null
  let heartbeatInterval = null
  let reconnectAttempts = 0
  const maxReconnectAttempts = 5

  // 计算属性
  const hasUnread = computed(() => unreadCount.value > 0)
  
  const latestNotification = computed(() => 
    notifications.value.length > 0 ? notifications.value[0] : null
  )

  const notificationsByType = computed(() => {
    const grouped = {}
    notifications.value.forEach(notif => {
      if (!grouped[notif.notification_type]) {
        grouped[notif.notification_type] = []
      }
      grouped[notif.notification_type].push(notif)
    })
    return grouped
  })

  // WebSocket连接管理
  function connectWebSocket() {
    if (wsConnected.value) return
    if (typeof window === 'undefined') return

    const token = localStorage.getItem('token') || localStorage.getItem('access_token')
    if (!token) {
      console.log('[Notifications] No token available, skipping WebSocket')
      return
    }

    // 检查是否配置了WebSocket端口，如果没有则不连接（避免连接到Vite服务器）
    const wsPort = import.meta.env.VITE_WS_PORT
    if (!wsPort || wsPort === window.location.port) {
      console.warn('[Notifications] WebSocket port not configured or same as dev server, skipping connection')
      return
    }

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = window.location.hostname
    const wsUrl = `${wsProtocol}//${wsHost}:${wsPort}/ws/notifications/?token=${token}`

    console.log('[Notifications] Connecting to WebSocket:', wsUrl.replace(token, '***'))

    try {
      websocket = new WebSocket(wsUrl)

      websocket.onopen = () => {
        console.log('[Notifications] ✅ WebSocket connected')
        wsConnected.value = true
        reconnectAttempts = 0
        
        startHeartbeat()
        fetchUnreadCount()
      }

      websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          handleWebSocketMessage(data)
        } catch (e) {
          console.error('[Notifications] Failed to parse message:', e)
        }
      }

      websocket.onclose = (event) => {
        console.log(`[Notifications] Connection closed: ${event.code}`)
        wsConnected.value = false
        stopHeartbeat()
        
        if (reconnectAttempts < maxReconnectAttempts) {
          reconnectAttempts++
          const delay = Math.min(1000 * reconnectAttempts, 30000)
          console.log(`[Notifications] Reconnecting in ${delay}ms... (attempt ${reconnectAttempts}/${maxReconnectAttempts})`)
          setTimeout(connectWebSocket, delay)
        }
      }

      websocket.onerror = (error) => {
        console.error('[Notifications] WebSocket error:', error)
        wsConnected.value = false
        // 立即关闭，避免连接挂起
        if (websocket) {
          websocket.close()
          websocket = null
        }
      }

    } catch (error) {
      console.error('[Notifications] Failed to create WebSocket:', error)
    }
  }

  function disconnectWebSocket() {
    stopHeartbeat()
    
    if (websocket) {
      websocket.close(1000, 'User disconnected')
      websocket = null
    }
    
    wsConnected.value = false
  }

  function startHeartbeat() {
    stopHeartbeat()
    heartbeatInterval = setInterval(() => {
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({ type: 'heartbeat' }))
      }
    }, 30000) // 每30秒发送一次心跳
  }

  function stopHeartbeat() {
    if (heartbeatInterval) {
      clearInterval(heartbeatInterval)
      heartbeatInterval = null
    }
  }

  function handleWebSocketMessage(data) {
    switch (data.type) {
      case 'connected':
        console.log('[Notifications] Server acknowledged connection')
        break

      case 'new_notification':
        handleNewNotification(data.payload)
        break

      case 'heartbeat_ack':
        // 心跳确认，无需处理
        break

      default:
        console.log('[Notifications] Unknown message type:', data.type)
    }
  }

  function handleNewNotification(payload) {
    console.log('[Notifications] 📨 New notification received:', payload.title)

    // 添加到列表顶部
    notifications.value.unshift({
      id: payload.id,
      title: payload.title,
      content: payload.content,
      notification_type: payload.notification_type,
      priority: payload.priority,
      is_read: false,
      link: payload.link,
      created_at: payload.created_at,
      metadata: payload.metadata || {},
      time_ago: '刚刚'
    })

    // 更新未读数量
    unreadCount.value++
    
    // 更新分类统计
    if (!unreadBreakdown.value[payload.notification_type]) {
      unreadBreakdown.value[payload.notification_type] = 0
    }
    unreadBreakdown.value[payload.notification_type]++

    // 显示浏览器通知（如果用户允许）
    showBrowserNotification(payload)
  }

  function showBrowserNotification(notification) {
    if ('Notification' in window && Notification.permission === 'granted') {
      try {
        new Notification(notification.title, {
          body: notification.content.replace(/<[^>]+>/g, '').substring(0, 100),
          icon: '/favicon.ico',
          tag: `notification-${notification.id}`
        })
      } catch (e) {
        console.warn('[Notifications] Failed to show browser notification:', e)
      }
    } else if ('Notification' in window && Notification.permission === 'default') {
      // 请求通知权限
      Notification.requestPermission()
    }
  }

  // API调用方法
  async function fetchNotifications(params = {}) {
    loading.value = true
    try {
      const response = await api.get('/notifications/', { params })
      
      if (response.data.code === 200) {
        notifications.value = response.data.data.results
        unreadCount.value = response.data.data.unread_count
        return response.data.data
      }
    } catch (error) {
      console.error('[Notifications] Failed to fetch:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchUnreadCount() {
    try {
      const response = await api.get('/notifications/unread_count/')
      
      if (response.data.code === 200) {
        unreadCount.value = response.data.data.count
        unreadBreakdown.value = response.data.data.breakdown
        return response.data.data
      }
    } catch (error) {
      console.error('[Notifications] Failed to fetch unread count:', error)
    }
  }

  async function markAsRead(notificationId) {
    try {
      const response = await api.put(`/notifications/${notificationId}/mark_read/`)
      
      if (response.data.code === 200) {
        // 更新本地状态
        const notif = notifications.value.find(n => n.id === notificationId)
        if (notif && !notif.is_read) {
          notif.is_read = true
          unreadCount.value = Math.max(0, unreadCount.value - 1)
          
          // 更新分类统计
          if (unreadBreakdown.value[notif.notification_type]) {
            unreadBreakdown.value[notif.notification_type]--
          }
        }
        
        return response.data.data
      }
    } catch (error) {
      console.error('[Notifications] Failed to mark as read:', error)
      throw error
    }
  }

  async function markAllAsRead() {
    try {
      const response = await api.post('/notifications/mark_all_read/')
      
      if (response.data.code === 200) {
        // 更新本地状态
        notifications.value.forEach(notif => {
          notif.is_read = true
        })
        unreadCount.value = 0
        Object.keys(unreadBreakdown.value).forEach(key => {
          unreadBreakdown.value[key] = 0
        })
        
        return response.data.data
      }
    } catch (error) {
      console.error('[Notifications] Failed to mark all as read:', error)
      throw error
    }
  }

  return {
    // 状态
    notifications,
    unreadCount,
    unreadBreakdown,
    loading,
    wsConnected,
    
    // 计算属性
    hasUnread,
    latestNotification,
    notificationsByType,
    
    // WebSocket方法
    connectWebSocket,
    disconnectWebSocket,
    
    // API方法
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead
  }
})
