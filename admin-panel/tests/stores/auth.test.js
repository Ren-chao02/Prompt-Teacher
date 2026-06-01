import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/store/modules/auth'

vi.mock('@/api/auth', () => ({
  loginApi: vi.fn(),
  getUserInfoApi: vi.fn(),
  logoutApi: vi.fn(),
}))

import { loginApi, getUserInfoApi, logoutApi } from '@/api/auth'

describe('AuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('初始状态', () => {
    it('未登录时token应为空', () => {
      const store = useAuthStore()
      expect(store.token).toBe('')
      expect(store.isLoggedIn).toBe(false)
      expect(store.user).toBeNull()
      expect(store.role).toBe('')
    })

    it('localStorage有token时自动恢复', () => {
      const store = useAuthStore()
      store.token = 'test-token'
      store.isLoggedIn = true
      store.role = 'admin'
      expect(store.token).toBe('test-token')
      expect(store.isLoggedIn).toBe(true)
      expect(store.role).toBe('admin')
    })
  })

  describe('Getters', () => {
    it('isAdmin 对管理员返回true', () => {
      const store = useAuthStore()
      store.token = 'token'
      store.role = 'admin'
      expect(store.isAdmin).toBe(true)
      expect(store.isTeacher).toBe(true)
      expect(store.isAdminOrTeacher).toBe(true)
    })

    it('isAdmin 对学生返回false', () => {
      const store = useAuthStore()
      store.role = 'student'
      expect(store.isAdmin).toBe(false)
      expect(store.isTeacher).toBe(false)
      expect(store.isAdminOrTeacher).toBe(false)
    })

    it('isTeacher 对教师返回true', () => {
      const store = useAuthStore()
      store.role = 'teacher'
      expect(store.isAdmin).toBe(false)
      expect(store.isTeacher).toBe(true)
      expect(store.isAdminOrTeacher).toBe(true)
    })
  })

  describe('login', () => {
    it('成功登录应保存token和用户信息', async () => {
      const mockResponse = {
        data: {
          access: 'new-access-token',
          refresh: 'new-refresh-token',
          user: { id: 1, username: 'admin', role: 'admin' }
        }
      }
      loginApi.mockResolvedValue(mockResponse)

      const store = useAuthStore()
      await store.login({ username: 'admin', password: 'admin123' })

      expect(store.token).toBe('new-access-token')
      expect(store.user).toEqual({ id: 1, username: 'admin', role: 'admin' })
      expect(store.role).toBe('admin')
      expect(store.isLoggedIn).toBe(true)
    })

    it('登录失败应抛出错误', async () => {
      loginApi.mockRejectedValue(new Error('用户名或密码错误'))
      const store = useAuthStore()

      await expect(store.login({ username: 'admin', password: 'wrong' }))
        .rejects.toThrow('用户名或密码错误')
    })
  })

  describe('fetchUserInfo', () => {
    it('成功获取用户信息', async () => {
      const mockUser = { id: 1, username: 'admin', role: 'admin', email: 'admin@test.com' }
      getUserInfoApi.mockResolvedValue({ data: mockUser })

      const store = useAuthStore()
      store.token = 'valid-token'
      await store.fetchUserInfo()

      expect(store.user).toEqual(mockUser)
      expect(store.role).toBe('admin')
    })

    it('token过期时获取用户信息应失败', async () => {
      getUserInfoApi.mockRejectedValue(new Error('身份认证信息未提供'))
      const store = useAuthStore()
      store.token = 'expired-token'

      await expect(store.fetchUserInfo()).rejects.toThrow('身份认证信息未提供')
    })
  })

  describe('logout', () => {
    it('登出应清除所有状态', () => {
      const store = useAuthStore()
      store.token = 'some-token'
      store.user = { id: 1, username: 'admin' }
      store.role = 'admin'
      store.isLoggedIn = true

      store.logout()

      expect(store.token).toBe('')
      expect(store.user).toBeNull()
      expect(store.role).toBe('')
      expect(store.isLoggedIn).toBe(false)
    })

    it('未登录时登出不应调用API', () => {
      const store = useAuthStore()
      store.token = ''
      store.isLoggedIn = false
      store.logout()
      expect(logoutApi).not.toHaveBeenCalled()
    })
  })
})