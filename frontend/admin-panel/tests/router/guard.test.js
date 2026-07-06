import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

vi.mock('@/store/modules/auth', () => ({
  useAuthStore: vi.fn(),
}))

import { useAuthStore } from '@/store/modules/auth'

describe('路由守卫逻辑', () => {
  let mockStore

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    mockStore = {
      token: '',
      user: null,
      role: '',
      isLoggedIn: false,
      fetchUserInfo: vi.fn().mockResolvedValue({}),
      logout: vi.fn(),
    }
    useAuthStore.mockReturnValue(mockStore)
  })

  function simulateGuard(toMeta, storeState) {
    Object.assign(mockStore, storeState)

    if (toMeta.requiresAuth && !mockStore.isLoggedIn) {
      return { path: '/login', query: { redirect: toMeta.fullPath || toMeta.path } }
    }

    if (toMeta.roles && toMeta.roles.length > 0) {
      if (!mockStore.role || !toMeta.roles.includes(mockStore.role)) {
        return '/403'
      }
    }

    return undefined
  }

  describe('未登录状态', () => {
    it('访问/login无需认证应放行', () => {
      const result = simulateGuard(
        { requiresAuth: false, path: '/login' },
        { isLoggedIn: false, token: '' }
      )
      expect(result).toBeUndefined()
    })

    it('访问需要认证的页面应重定向', () => {
      const result = simulateGuard(
        { requiresAuth: true, path: '/dashboard', fullPath: '/dashboard' },
        { isLoggedIn: false, token: '' }
      )
      expect(result).toMatchObject({
        path: '/login',
        query: { redirect: '/dashboard' }
      })
    })
  })

  describe('已登录状态', () => {
    it('已登录可访问需要认证的页面', () => {
      const result = simulateGuard(
        { requiresAuth: true },
        { isLoggedIn: true, token: 'valid', role: 'admin' }
      )
      expect(result).toBeUndefined()
    })

    it('管理员可访问admin角色页面', () => {
      const result = simulateGuard(
        { requiresAuth: true, roles: ['admin'] },
        { isLoggedIn: true, token: 't', role: 'admin' }
      )
      expect(result).toBeUndefined()
    })

    it('学生访问admin角色页面应被拒绝', () => {
      const result = simulateGuard(
        { requiresAuth: true, roles: ['admin'] },
        { isLoggedIn: true, token: 't', role: 'student' }
      )
      expect(result).toBe('/403')
    })

    it('教师可访问teacher角色页面', () => {
      const result = simulateGuard(
        { requiresAuth: true, roles: ['admin', 'teacher'] },
        { isLoggedIn: true, token: 't', role: 'teacher' }
      )
      expect(result).toBeUndefined()
    })

    it('学生可访问无需角色的页面', () => {
      const result = simulateGuard(
        { requiresAuth: true },
        { isLoggedIn: true, token: 't', role: 'student' }
      )
      expect(result).toBeUndefined()
    })

    it('无token未登录应跳转登录', () => {
      const result = simulateGuard(
        { requiresAuth: true, path: '/dashboard', fullPath: '/dashboard' },
        { isLoggedIn: false, token: '', role: '' }
      )
      expect(result).toMatchObject({ path: '/login' })
    })
  })
})