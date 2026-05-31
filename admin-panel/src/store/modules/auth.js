import { defineStore } from 'pinia'
import { loginApi, getUserInfoApi, logoutApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null,
    role: localStorage.getItem('user_role') || '',
    isLoggedIn: !!localStorage.getItem('token')
  }),

  getters: {
    isAdmin: (state) => state.role === 'admin',
    isTeacher: (state) => ['admin', 'teacher'].includes(state.role),
    isAdminOrTeacher: (state) => ['admin', 'teacher'].includes(state.role)
  },

  actions: {
    async login(credentials) {
      const res = await loginApi(credentials)
      const data = res.data
      
      this.token = data.access
      this.role = data.user.role
      this.user = data.user
      this.isLoggedIn = true
      
      localStorage.setItem('token', data.access)
      localStorage.setItem('refresh_token', data.refresh)
      localStorage.setItem('user_role', data.user.role)
      
      return data
    },

    async fetchUserInfo() {
      const res = await getUserInfoApi()
      this.user = res.data
      this.role = res.data.role
      
      localStorage.setItem('user_role', res.data.role)
    },

    logout() {
      try {
        if (this.token) {
          logoutApi({ refresh: localStorage.getItem('refresh_token') })
        }
      } catch (e) {
        console.error('Logout error:', e)
      }
      
      this.token = ''
      this.user = null
      this.role = ''
      this.isLoggedIn = false
      
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_role')
    }
  }
})
