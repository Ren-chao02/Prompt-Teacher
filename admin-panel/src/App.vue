<template>
  <router-view />
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth'

const router = useRouter()
const authStore = useAuthStore()
const isInitialized = ref(false)

onMounted(async () => {
  if (authStore.token && !authStore.user) {
    try {
      await authStore.fetchUserInfo()
      console.log('✅ 用户信息已恢复')
    } catch (error) {
      console.error('❌ 恢复用户信息失败:', error)
      authStore.logout()
      router.push('/admin/login')
    }
  }
  
  isInitialized.value = true
})
</script>
