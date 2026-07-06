<template>
  <div id="admin-app">
    <div v-if="error" style="padding: 30px; background: #fff3f3; border: 2px solid #ff4444; margin: 20px; border-radius: 8px;">
      <h2 style="color: #cc0000; margin-top: 0;">❌ 应用加载错误</h2>
      <pre style="background: #f5f5f5; padding: 15px; border-radius: 4px; overflow: auto; max-height: 300px; white-space: pre-wrap;">{{ error }}</pre>
      <p style="margin-top: 15px;">
        <a href="/admin/login/" style="color: #409EFF;">→ 直接访问登录页面</a>
      </p>
    </div>
    
    <div v-if="isReady && !error">
      <router-view />
    </div>
    
    <div v-if="!isReady && !error" style="padding: 40px; text-align: center; color: #666;">
      <div style="font-size: 48px; margin-bottom: 16px;">⏳</div>
      <p style="font-size: 18px;">正在加载管理后台...</p>
      <p style="font-size: 14px; color: #999;">如果长时间无响应，请检查浏览器控制台</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onErrorCaptured } from 'vue'

const isReady = ref(false)
const error = ref(null)

onErrorCaptured((err, instance, info) => {
  console.error('🔥 应用级错误:', err, info)
  error.value = `错误: ${err.message}\n堆栈: ${err.stack}\n组件: ${info}`
  return false
})

window.addEventListener('error', (e) => {
  console.error('🔥 全局错误:', e.error || e.message)
  if (!error.value) {
    error.value = `全局错误: ${e.error?.stack || e.message}`
  }
})

window.addEventListener('unhandledrejection', (e) => {
  console.error('🔥 Promise错误:', e.reason)
  if (!error.value) {
    error.value = `Promise错误: ${e.reason?.stack || e.reason}`
  }
})

console.log('🚀 App.vue 已启动')
console.log('📍 当前URL:', window.location.href)

onMounted(async () => {
  try {
    console.log('🔄 开始初始加载...')
    
    // 延迟一小段时间确认路由挂载
    await new Promise(resolve => setTimeout(resolve, 100))
    
    console.log('✅ Vue Router 已初始化')
    console.log('📍 路由路径:', window.location.pathname)
  } catch (e) {
    console.error('❌ 初始化失败:', e)
    error.value = e.message
  } finally {
    isReady.value = true
    console.log('✅ 加载完成')
  }
})
</script>

<style>
body { margin: 0; padding: 0; }
#admin-app { min-height: 100vh; }
</style>