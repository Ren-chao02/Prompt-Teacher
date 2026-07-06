/**
 * Vitest 全局设置文件
 * 
 * 功能:
 * - 模拟浏览器API (localStorage, sessionStorage)
 * - 配置全局测试工具
 * - 设置Element Plus组件库
 */

import { config } from '@vue/test-utils'
import ElementPlus from 'element-plus'

// 模拟 localStorage
const localStorageMock = {
  getItem: vi.fn(() => null),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}

// 模拟 sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(() => null),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}

// 挂载到全局
Object.defineProperty(globalThis, 'localStorage', {
  value: localStorageMock,
})

Object.defineProperty(globalThis, 'sessionStorage', {
  value: sessionStorageMock,
})

// 模拟 window.location
Object.defineProperty(globalThis, 'location', {
  value: {
    href: 'http://localhost:5173/',
    origin: 'http://localhost:5173',
    pathname: '/',
    search: '',
    hash: '',
    reload: vi.fn(),
    assign: vi.fn(),
    replace: vi.fn(),
  },
  writable: true,
})

// 模拟 IntersectionObserver（用于滚动加载等）
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
}

// 模拟 ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
}

// 模拟 matchMedia
window.matchMedia = (query) => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: vi.fn(),
  removeListener: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  dispatchEvent: vi.fn(),
})

// 配置 Vue Test Utils 全局选项
config.global.plugins = [ElementPlus]

// 全局存根（stub）配置
config.global.stubs = {
  // 可以在这里添加需要存根的组件
  // 'el-button': true,
  // 'router-link': true,
}

// 输出测试环境信息
console.log('✅ 测试环境初始化完成')
console.log('   - localStorage/sessionStorage 已模拟')
console.log('   - Element Plus 已注册')
console.log('   - 浏览器 API 已模拟')
