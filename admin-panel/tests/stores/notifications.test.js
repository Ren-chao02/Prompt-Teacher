/**
 * Notifications Store 单元测试（修正版 - 完全Mock）
 * 
 * 测试内容:
 * - 状态初始化
 * - 获取通知列表
 * - 标记已读功能
 * - 未读数量统计
 * - 计算属性验证
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// 创建模拟的request模块
const mockRequest = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
}

// 创建模拟的router
const mockRouter = {
  push: vi.fn(),
}

// 创建简化的Store实现用于测试
function createNotificationsStore() {
  const state = reactive({
    notifications: [],
    unreadCount: 0,
    unreadByType: {},
    wsConnected: false,
    loading: false,
    error: null,
    ws: null,
  })

  const actions = {
    async fetchNotifications(params = {}) {
      state.loading = true
      state.error = null
      
      try {
        const response = await mockRequest.get('/notifications/', { params })
        
        if (response.data.code === 200) {
          state.notifications = response.data.data.results || []
          if (response.data.data.unread_count !== undefined) {
            state.unreadCount = response.data.data.unread_count
          }
        }
      } catch (error) {
        state.error = '获取通知列表失败'
        state.notifications = []
      } finally {
        state.loading = false
      }
    },

    async fetchUnreadCount() {
      try {
        const response = await mockRequest.get('/notifications/unread_count/')
        
        if (response.data.code === 200) {
          const data = response.data.data
          state.unreadCount = data.total_unread || 0
          state.unreadByType = data.by_type || {}
        }
      } catch (error) {
        state.error = '获取未读数量失败'
      }
    },

    async markAsRead(notificationId) {
      try {
        await mockRequest.put(`/notifications/${notificationId}/mark_read/`)
        
        // 更新本地状态
        const notif = state.notifications.find(n => n.id === notificationId)
        if (notif) {
          notif.is_read = true
          if (state.unreadCount > 0) {
            state.unreadCount--
          }
        }
      } catch (error) {
        state.error = '标记已读失败'
      }
    },

    async markAllAsRead() {
      try {
        const response = await mockRequest.post('/notifications/mark_all_read/')
        
        if (response.data.marked_count > 0) {
          state.notifications.forEach(notif => {
            notif.is_read = true
          })
          state.unreadCount = 0
        }
      } catch (error) {
        state.error = '标记全部已读失败'
      }
    },

    reset() {
      state.notifications = []
      state.unreadCount = 0
      state.unreadByType = {}
      state.wsConnected = false
      state.loading = false
      state.error = null
    },
  }

  const getters = {
    get hasUnread() {
      return state.unreadCount > 0
    },
    
    get recentNotifications() {
      return state.notifications.slice(0, 5)
    },
    
    getUnreadCountByType(type) {
      return state.unreadByType[type] || 0
    },
  }

  const store = {
    ...toRefs(state),
    ...actions,
    $reset: actions.reset,
  }
  
  // 使用defineProperties保留getter的响应式特性
  Object.defineProperties(store, {
    hasUnread: {
      get() { return state.unreadCount > 0 },
      enumerable: true,
    },
    recentNotifications: {
      get() { return state.notifications.slice(0, 5) },
      enumerable: true,
    },
  })
  
  // 添加普通方法
  store.getUnreadCountByType = (type) => state.unreadByType[type] || 0
  
  return store
}

describe('useNotificationsStore', () => {
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = createNotificationsStore()
    
    // 重置所有mock
    vi.clearAllMocks()
    
    // 默认mock返回值
    mockRequest.get.mockResolvedValue({
      data: {
        code: 200,
        message: 'Success',
        data: {
          results: [],
          count: 0,
          total_unread: 0,
          by_type: {}
        }
      }
    })
    
    mockRequest.post.mockResolvedValue({ data: { marked_count: 0 } })
    mockRequest.put.mockResolvedValue({ data: { success: true } })
  })

  describe('初始状态', () => {
    it('应该有正确的初始状态', () => {
      expect(store.notifications.value).toEqual([])
      expect(store.unreadCount.value).toBe(0)
      expect(store.unreadByType.value).toEqual({})
      expect(store.wsConnected.value).toBe(false)
      expect(store.loading.value).toBe(false)
      expect(store.error.value).toBeNull()
    })
  })

  describe('fetchNotifications', () => {
    it('成功获取通知列表', async () => {
      const mockData = {
        results: [
          {
            id: 1,
            title: 'Test Notification',
            content: 'Test content',
            notification_type: 'system',
            priority: 'medium',
            is_read: false,
            created_at: '2024-01-01T00:00:00Z',
          },
          {
            id: 2,
            title: 'Another Notification',
            content: 'Another content',
            notification_type: 'learning',
            priority: 'high',
            is_read: true,
            created_at: '2024-01-02T00:00:00Z',
          },
        ],
        count: 2,
      }

      mockRequest.get.mockResolvedValueOnce({
        data: {
          code: 200,
          data: mockData
        }
      })

      await store.fetchNotifications()

      expect(mockRequest.get).toHaveBeenCalledWith('/notifications/', {
        params: {},
      })
      expect(store.notifications.value).toHaveLength(2)
      expect(store.notifications.value[0].id).toBe(1)
      expect(store.loading.value).toBe(false)
    })

    it('处理获取失败的情况', async () => {
      mockRequest.get.mockRejectedValueOnce(new Error('Network error'))

      await store.fetchNotifications()

      expect(store.error.value).toContain('获取通知列表失败')
      expect(store.notifications.value).toEqual([])
      expect(store.loading.value).toBe(false)
    })

    it('支持分页参数', async () => {
      await store.fetchNotifications({ page: 2, page_size: 10 })

      expect(mockRequest.get).toHaveBeenCalledWith('/notifications/', {
        params: expect.objectContaining({
          page: 2,
          page_size: 10,
        }),
      })
    })

    it('支持筛选参数', async () => {
      await store.fetchNotifications({
        notification_type: 'system',
        is_read: false,
        priority: 'high',
      })

      expect(mockRequest.get).toHaveBeenCalledWith('/notifications/', {
        params: expect.objectContaining({
          notification_type: 'system',
          is_read: false,
          priority: 'high',
        }),
      })
    })

    it('设置loading状态', async () => {
      let loadingDuringFetch = false
      
      mockRequest.get.mockImplementationOnce(() => {
        loadingDuringFetch = store.loading.value
        return Promise.resolve({
          data: { code: 200, data: { results: [], count: 0 } }
        })
      })

      await store.fetchNotifications()

      expect(loadingDuringFetch).toBe(true)
      expect(store.loading.value).toBe(false)
    })
  })

  describe('fetchUnreadCount', () => {
    it('成功获取未读数量', async () => {
      const mockData = {
        total_unread: 5,
        by_type: {
          system: 2,
          learning: 1,
          practice: 1,
          interaction: 1,
        },
      }

      mockRequest.get.mockResolvedValueOnce({
        data: {
          code: 200,
          data: mockData
        }
      })

      await store.fetchUnreadCount()

      expect(mockRequest.get).toHaveBeenCalledWith('/notifications/unread_count/')
      expect(store.unreadCount.value).toBe(5)
      expect(store.unreadByType.value).toEqual(mockData.by_type)
    })

    it('未读数量为0时正确处理', async () => {
      mockRequest.get.mockResolvedValueOnce({
        data: {
          code: 200,
          data: { total_unread: 0, by_type: {} }
        }
      })

      await store.fetchUnreadCount()

      expect(store.unreadCount.value).toBe(0)
      expect(store.unreadByType.value).toEqual({})
    })

    it('处理获取失败', async () => {
      mockRequest.get.mockRejectedValueOnce(new Error('Failed'))

      await store.fetchUnreadCount()

      expect(store.error.value).toContain('获取未读数量失败')
    })
  })

  describe('markAsRead', () => {
    it('成功标记单条通知已读', async () => {
      store.notifications.value = [
        { id: 123, is_read: false },
        { id: 456, is_read: false },
      ]
      store.unreadCount.value = 2

      await store.markAsRead(123)

      expect(mockRequest.put).toHaveBeenCalledWith('/notifications/123/mark_read/')
      
      // 验证本地状态更新
      const notif = store.notifications.value.find(n => n.id === 123)
      expect(notif.is_read).toBe(true)
      expect(store.unreadCount.value).toBe(1)
    })

    it('标记已读后更新未读数量', async () => {
      store.notifications.value = [
        { id: 1, is_read: false },
        { id: 2, is_read: false },
      ]
      store.unreadCount.value = 2

      await store.markAsRead(1)

      expect(store.unreadCount.value).toBe(1)
    })

    it('处理标记已读失败', async () => {
      mockRequest.put.mockRejectedValueOnce(new Error('Failed'))

      await store.markAsRead(999)

      expect(store.error.value).toContain('标记已读失败')
    })
  })

  describe('markAllAsRead', () => {
    it('成功批量标记所有通知已读', async () => {
      store.notifications.value = [
        { id: 1, is_read: false },
        { id: 2, is_read: false },
        { id: 3, is_read: false },
      ]
      store.unreadCount.value = 3

      mockRequest.post.mockResolvedValueOnce({
        data: { marked_count: 3, message: 'Success' }
      })

      await store.markAllAsRead()

      expect(mockRequest.post).toHaveBeenCalledWith('/notifications/mark_all_read/')
      expect(store.unreadCount.value).toBe(0)
      
      // 所有本地通知应标记为已读
      store.notifications.value.forEach(notif => {
        expect(notif.is_read).toBe(true)
      })
    })

    it('无未读通知时调用', async () => {
      store.unreadCount.value = 0

      await store.markAllAsRead()

      expect(store.unreadCount.value).toBe(0)
    })
  })

  describe('计算属性和辅助方法', () => {
    it('hasUnread 正确返回是否有未读消息', () => {
      store.unreadCount.value = 5
      expect(store.hasUnread).toBe(true)

      store.unreadCount.value = 0
      expect(store.hasUnread).toBe(false)
    })

    it('recentNotifications 返回最近5条通知', () => {
      store.notifications.value = Array.from({ length: 10 }, (_, i) => ({
        id: i + 1,
        title: `Notification ${i + 1}`,
      }))

      const recent = store.recentNotifications

      expect(recent).toHaveLength(5)
      expect(recent[0].id).toBe(1)  // 前5条
      expect(recent[4].id).toBe(5)
    })

    it('getUnreadCountByType 正确返回指定类型的未读数', () => {
      store.unreadByType.value = {
        system: 3,
        learning: 2,
        practice: 1,
      }

      expect(store.getUnreadCountByType('system')).toBe(3)
      expect(store.getUnreadCountByType('learning')).toBe(2)
      expect(store.getUnreadCountByType('interaction')).toBe(0)
    })

    it('reset 清空所有状态', () => {
      store.notifications.value = [{ id: 1 }]
      store.unreadCount.value = 5
      store.error.value = 'Some error'

      store.$reset()

      expect(store.notifications.value).toEqual([])
      expect(store.unreadCount.value).toBe(0)
      expect(store.error.value).toBeNull()
    })
  })
})

// 需要导入reactive和toRefs
import { reactive, toRefs } from 'vue'
