import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/modules/auth'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

service.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  (response) => {
    const res = response.data

    const showError = response.config.showError !== false

    if (res.code && ![200, 201].includes(res.code)) {
      if (showError) {
        const message = res.message || '请求失败'

        if (message.length < 100) {
          ElMessage.error(message)
        } else {
          ElMessage.error('操作失败，请稍后重试')
        }
      }

      if (res.code === 401) {
        const authStore = useAuthStore()
        authStore.logout()
        window.location.href = '/admin/login/'
      }

      return Promise.reject(new Error(res.message || '请求失败'))
    }

    return res
  },
  (error) => {
    console.error('Response error:', error)
    
    const showError = error.config?.showError !== false
    
    if (error.response) {
      const status = error.response.status
      const data = error.response.data
      
      if (showError) {
        switch (status) {
          case 401:
            ElMessage.error('登录已过期，请重新登录')
            break
          case 403:
            ElMessage.error('没有权限访问此资源')
            break
          case 404:
            ElMessage.error('请求的资源不存在')
            break
          case 422:
            if (data?.detail) {
              const detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
              // 只显示简短的验证错误
              ElMessage.error(detail.length > 50 ? '数据验证失败' : detail)
            } else {
              ElMessage.error('数据验证失败')
            }
            break
          case 500:
            ElMessage.error('服务器内部错误，请稍后重试')
            break
          default:
            // 对于其他错误，使用通用消息
            const errorMsg = data?.message || data?.detail || `请求错误 (${status})`
            ElMessage.error(errorMsg.length > 50 ? '操作失败，请稍后重试' : errorMsg)
        }
      }
      
      if (status === 401) {
        const authStore = useAuthStore()
        authStore.logout()
        window.location.href = '/admin/login/'
      }

      return Promise.reject({
        message: data?.message || data?.detail || `HTTP ${status}`,
        status,
        data
      })
    } else if (error.request) {
      if (showError) {
        ElMessage.error('网络连接失败，请检查网络')
      }
      return Promise.reject({ message: '网络连接失败' })
    } else {
      if (showError) {
        ElMessage.error(error.message || '请求配置错误')
      }
      return Promise.reject(error)
    }
  }
)

export default service
