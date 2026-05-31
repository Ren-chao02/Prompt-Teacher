<template>
  <div v-if="isInitialized || !authStore.token" class="app-wrapper">
    <router-view />
  </div>
  <div v-else class="loading-screen">
    <div class="loading-content">
      <el-icon class="loading-icon" :size="48"><Loading /></el-icon>
      <p>正在加载...</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth'
import { Loading } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const isInitialized = ref(false)

onMounted(async () => {
  try {
    if (authStore.token && !authStore.user) {
      console.log('🔄 正在恢复用户信息...')
      await authStore.fetchUserInfo()
      console.log('✅ 用户信息已恢复')
    }
  } catch (error) {
    console.error('❌ 恢复用户信息失败:', error)
    
    // 不要立即logout，让用户可以看到登录页面
    if (error.response?.status === 401) {
      authStore.logout()
    }
  } finally {
    // 无论成功失败都要标记为已初始化，避免永久显示loading
    isInitialized.value = true
  }
})
</script>

<style scoped>
.app-wrapper {
  min-height: 100vh;
}

.loading-screen {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.loading-content {
  text-align: center;
  color: #606266;
}

.loading-icon {
  animation: rotate 1.5s linear infinite;
  margin-bottom: 16px;
  color: #409EFF;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
