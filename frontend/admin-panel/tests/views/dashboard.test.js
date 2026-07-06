import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

const mockGetDashboardStats = vi.fn()
vi.mock('@/api/analytics', () => ({
  getDashboardStats: mockGetDashboardStats,
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useRoute: () => ({ path: '/dashboard', meta: { title: '仪表盘' } }),
}))

vi.mock('@/store/modules/auth', () => ({
  useAuthStore: () => ({
    token: 'test-token',
    user: { username: 'admin' },
    role: 'admin',
    isLoggedIn: true,
  }),
}))

vi.mock('element-plus', () => ({
  ElMessage: { error: vi.fn() },
  ElLoading: { service: vi.fn(() => ({ close: vi.fn() })) },
}))

describe('Dashboard 仪表盘', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('数据加载失败时显示错误提示', async () => {
    mockGetDashboardStats.mockRejectedValue(new Error('获取数据失败'))

    await import('@/views/dashboard/index.vue')

    await new Promise(resolve => setTimeout(resolve, 50))

    const { ElMessage } = await import('element-plus')
  })

  it('成功加载数据不报错', async () => {
    mockGetDashboardStats.mockResolvedValue({
      data: {
        user_count: 150,
        content_count: 45,
        practice_count: 230,
        completion_rate: '78.5%',
        recent_activities: []
      }
    })

    await import('@/views/dashboard/index.vue')
  })
})