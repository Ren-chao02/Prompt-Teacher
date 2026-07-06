import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useRoute: () => ({
    path: '/dashboard',
    meta: { title: '仪表盘' },
    matched: [{ meta: { title: '仪表盘' } }],
  }),
}))

const mockFetchUserInfo = vi.fn()
const mockLogout = vi.fn()
vi.mock('@/store/modules/auth', () => ({
  useAuthStore: () => ({
    token: 'test-token',
    user: { id: 1, username: 'admin', avatar: null },
    role: 'admin',
    isLoggedIn: true,
    isAdmin: true,
    isAdminOrTeacher: true,
    isTeacher: false,
    fetchUserInfo: mockFetchUserInfo,
    logout: mockLogout,
  }),
}))

vi.mock('@/components/NotificationBell.vue', () => ({
  default: { template: '<div class="notification-bell">Bell</div>' },
}))

const epStubs = {
  'el-container': { template: '<div><slot /></div>' },
  'el-aside': { template: '<div><slot /></div>' },
  'el-header': { template: '<div><slot /></div>' },
  'el-main': { template: '<div><slot /></div>' },
  'el-menu': { template: '<div><slot /></div>' },
  'el-menu-item': { template: '<div><slot /></div>' },
  'el-sub-menu': { template: '<div><slot /></div>' },
  'el-icon': { template: '<div><slot /></div>' },
  'el-scrollbar': { template: '<div><slot /></div>' },
  'el-breadcrumb': { template: '<div><slot /></div>' },
  'el-breadcrumb-item': { template: '<div><slot /></div>' },
  'el-dropdown': { template: '<div><slot /></div>' },
  'el-dropdown-menu': { template: '<div><slot /></div>' },
  'el-dropdown-item': { template: '<div><slot /></div>' },
  'el-avatar': { template: '<div><slot /></div>' },
  'el-tag': { template: '<div><slot /></div>' },
  'el-tooltip': { template: '<div><slot /></div>' },
  'router-view': { template: '<div class="router-view"><slot /></div>' },
  'router-link': { template: '<a><slot /></a>' },
}

import AdminLayout from '@/components/Layout/AdminLayout.vue'

describe('AdminLayout 管理后台布局', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  describe('菜单权限', () => {
    it('管理员菜单包含用户管理', () => {
      const wrapper = mount(AdminLayout, { global: { stubs: epStubs } })
      const menuPaths = wrapper.vm.menuList.map(m => m.path)
      expect(menuPaths).toContain('/users/list')
    })

    it('仪表盘对所有角色可见', () => {
      const wrapper = mount(AdminLayout, { global: { stubs: epStubs } })
      expect(wrapper.vm.hasPermission({ roles: ['admin', 'teacher', 'student'] })).toBe(true)
    })

    it('用户管理仅管理员可见', () => {
      const wrapper = mount(AdminLayout, { global: { stubs: epStubs } })
      expect(wrapper.vm.hasPermission({ roles: ['admin'] })).toBe(true)
      expect(wrapper.vm.hasPermission({ roles: ['teacher'] })).toBe(false)
      expect(wrapper.vm.hasPermission({ roles: ['student'] })).toBe(false)
    })

    it('创建内容对管理员和教师可见', () => {
      const wrapper = mount(AdminLayout, { global: { stubs: epStubs } })
      expect(wrapper.vm.hasPermission({ roles: ['admin', 'teacher'] })).toBe(true)
    })
  })

  describe('getRoleLabel', () => {
    it('应返回正确的中文角色名', () => {
      const wrapper = mount(AdminLayout, { global: { stubs: epStubs } })
      expect(wrapper.vm.getRoleLabel('admin')).toBe('管理员')
      expect(wrapper.vm.getRoleLabel('teacher')).toBe('教师')
      expect(wrapper.vm.getRoleLabel('student')).toBe('学生')
    })
  })

  describe('getRoleTagType', () => {
    it('应返回正确的Tag类型', () => {
      const wrapper = mount(AdminLayout, { global: { stubs: epStubs } })
      expect(wrapper.vm.getRoleTagType('admin')).toBe('danger')
      expect(wrapper.vm.getRoleTagType('teacher')).toBe('warning')
      expect(wrapper.vm.getRoleTagType('student')).toBe('info')
    })
  })

  describe('toggleCollapse', () => {
    it('切换折叠状态', () => {
      const wrapper = mount(AdminLayout, { global: { stubs: epStubs } })
      wrapper.vm.isCollapse = false
      wrapper.vm.toggleCollapse()
      expect(wrapper.vm.isCollapse).toBe(true)
    })
  })

  describe('页面标题', () => {
    it('随路由变化', () => {
      mount(AdminLayout, { global: { stubs: epStubs } })
      expect(document.title).toContain('仪表盘')
    })
  })
})