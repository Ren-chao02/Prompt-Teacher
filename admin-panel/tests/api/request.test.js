import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

vi.mock('element-plus', () => ({
  ElMessage: { error: vi.fn(), success: vi.fn() }
}))

import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/modules/auth'

describe('API请求拦截器 - 请求拦截器', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('有token时添加Authorization头', async () => {
    const { default: service } = await import('@/api/request')

    const store = useAuthStore()
    store.token = 'my-token'

    const handler = service.interceptors.request.handlers[0]
    const config = { headers: {} }
    const result = await handler.fulfilled(config)

    expect(result.headers.Authorization).toBe('Bearer my-token')
  })

  it('无token时不添加Authorization头', async () => {
    const { default: service } = await import('@/api/request')

    const handler = service.interceptors.request.handlers[0]
    const config = { headers: {} }
    const result = await handler.fulfilled(config)

    expect(result.headers.Authorization).toBeUndefined()
  })
})

describe('API请求拦截器 - 成功响应', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('code 200直接返回', async () => {
    const { default: service } = await import('@/api/request')
    const handler = service.interceptors.response.handlers[0]

    const response = { data: { code: 200, data: 'ok' }, config: {} }
    const result = await handler.fulfilled(response)

    expect(result).toEqual({ code: 200, data: 'ok' })
    expect(ElMessage.error).not.toHaveBeenCalled()
  })

  it('code 201直接返回', async () => {
    const { default: service } = await import('@/api/request')
    const handler = service.interceptors.response.handlers[0]

    const response = { data: { code: 201, data: 'created' }, config: {} }
    const result = await handler.fulfilled(response)
    expect(result).toEqual({ code: 201, data: 'created' })
  })

  it('code 400显示错误消息并reject', async () => {
    const { default: service } = await import('@/api/request')
    const handler = service.interceptors.response.handlers[0]

    const response = { data: { code: 400, message: '参数错误' }, config: {} }
    await expect(handler.fulfilled(response)).rejects.toThrow('参数错误')
    expect(ElMessage.error).toHaveBeenCalledWith('参数错误')
  })

  it('code 401触发登出', async () => {
    const { default: service } = await import('@/api/request')
    const handler = service.interceptors.response.handlers[0]

    const response = { data: { code: 401, message: '未授权' }, config: {} }
    await expect(handler.fulfilled(response)).rejects.toThrow('未授权')
    expect(ElMessage.error).toHaveBeenCalled()
  })
})

describe('API请求拦截器 - HTTP错误', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('401错误', async () => {
    const { default: service } = await import('@/api/request')
    const handler = service.interceptors.response.handlers[0]

    const error = {
      response: { status: 401, data: { detail: '未授权' } },
      config: {}
    }

    const result = await handler.rejected(error).catch(e => e)
    expect(result).toMatchObject({ message: '未授权', status: 401 })
    expect(ElMessage.error).toHaveBeenCalledWith('登录已过期，请重新登录')
  })

  it('403错误', async () => {
    const { default: service } = await import('@/api/request')
    const handler = service.interceptors.response.handlers[0]

    const error = {
      response: { status: 403, data: { detail: '禁止访问' } },
      config: {}
    }

    const result = await handler.rejected(error).catch(e => e)
    expect(result).toMatchObject({ message: '禁止访问', status: 403 })
    expect(ElMessage.error).toHaveBeenCalledWith('没有权限访问此资源')
  })

  it('404错误', async () => {
    const { default: service } = await import('@/api/request')
    const handler = service.interceptors.response.handlers[0]

    const error = {
      response: { status: 404, data: { detail: '未找到' } },
      config: {}
    }

    const result = await handler.rejected(error).catch(e => e)
    expect(result).toMatchObject({ message: '未找到', status: 404 })
    expect(ElMessage.error).toHaveBeenCalledWith('请求的资源不存在')
  })

  it('500错误', async () => {
    const { default: service } = await import('@/api/request')
    const handler = service.interceptors.response.handlers[0]

    const error = {
      response: { status: 500, data: {} },
      config: {}
    }

    const result = await handler.rejected(error).catch(e => e)
    expect(result.status).toBe(500)
    expect(ElMessage.error).toHaveBeenCalledWith('服务器内部错误，请稍后重试')
  })

  it('网络错误', async () => {
    const { default: service } = await import('@/api/request')
    const handler = service.interceptors.response.handlers[0]

    const error = { request: {}, config: {}, message: 'Network Error' }

    const result = await handler.rejected(error).catch(e => e)
    expect(result.message).toBe('网络连接失败')
    expect(ElMessage.error).toHaveBeenCalledWith('网络连接失败，请检查网络')
  })

  it('showError为false不显示错误', async () => {
    const { default: service } = await import('@/api/request')
    const handler = service.interceptors.response.handlers[0]

    const error = {
      response: { status: 500, data: {} },
      config: { showError: false }
    }

    await handler.rejected(error).catch(e => e)
    expect(ElMessage.error).not.toHaveBeenCalled()
  })
})