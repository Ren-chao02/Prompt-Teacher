import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'

const mockRouterPush = vi.fn()
const mockRouteQuery = { redirect: '/dashboard' }

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockRouterPush }),
  useRoute: () => ({ query: mockRouteQuery }),
}))

const mockLogin = vi.fn()
vi.mock('@/store/modules/auth', () => ({
  useAuthStore: () => ({
    login: mockLogin,
    token: '',
    user: null,
    role: '',
    isLoggedIn: false,
  }),
}))

import LoginPage from '@/views/login/index.vue'

function createWrapper() {
  return mount(LoginPage, {
    global: {
      stubs: {
        'el-form': { template: '<div><slot /></div>' },
        'el-form-item': { template: '<div><slot /></div>' },
        'el-input': { template: '<input />' },
        'el-button': { template: '<button><slot /></button>' },
      }
    }
  })
}

describe('LoginPage 登录页', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('应渲染标题', () => {
    const wrapper = createWrapper()
    expect(wrapper.find('.title').text()).toBe('Prompt Teacher')
    expect(wrapper.find('.subtitle').text()).toBe('后台管理系统')
  })

  it('应渲染登录按钮', () => {
    const wrapper = createWrapper()
    expect(wrapper.find('.login-button').exists()).toBe(true)
    expect(wrapper.find('.login-button').text()).toBe('登 录')
  })

  it('登录按钮加载中状态', async () => {
    const wrapper = createWrapper()
    wrapper.vm.loading = true
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.login-button').text()).toBe('登录中...')
  })

  it('登录成功跳转dashboard', async () => {
    mockLogin.mockResolvedValue({})
    const wrapper = createWrapper()
    wrapper.vm.loginForm.username = 'admin'
    wrapper.vm.loginForm.password = 'admin123'
    wrapper.vm.loginFormRef = { validate: vi.fn(() => Promise.resolve(true)) }

    await wrapper.vm.handleLogin()

    expect(mockLogin).toHaveBeenCalledWith({
      username: 'admin',
      password: 'admin123',
    })
    expect(mockRouterPush).toHaveBeenCalledWith('/dashboard')
  })

  it('登录成功使用redirect参数', async () => {
    mockRouteQuery.redirect = '/learning/list'
    mockLogin.mockResolvedValue({})

    const wrapper = createWrapper()
    wrapper.vm.loginForm.username = 'admin'
    wrapper.vm.loginForm.password = 'admin123'
    wrapper.vm.loginFormRef = { validate: vi.fn(() => Promise.resolve(true)) }

    await wrapper.vm.handleLogin()

    expect(mockLogin).toHaveBeenCalled()
    expect(mockRouterPush).toHaveBeenCalledWith('/learning/list')
  })

  it('登录失败不跳转', async () => {
    mockLogin.mockRejectedValue(new Error('用户名或密码错误'))
    const wrapper = createWrapper()
    wrapper.vm.loginForm.username = 'admin'
    wrapper.vm.loginForm.password = 'wrong'
    wrapper.vm.loginFormRef = { validate: vi.fn(() => Promise.resolve(true)) }

    await wrapper.vm.handleLogin()

    expect(mockLogin).toHaveBeenCalled()
    expect(mockRouterPush).not.toHaveBeenCalled()
  })

  it('表单验证失败不调用login', async () => {
    const wrapper = createWrapper()
    wrapper.vm.loginFormRef = { validate: vi.fn(() => Promise.resolve(false)) }

    await wrapper.vm.handleLogin()

    expect(mockLogin).not.toHaveBeenCalled()
  })
})