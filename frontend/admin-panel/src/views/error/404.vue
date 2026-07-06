<template>
  <div class="error-page">
    <div class="error-code">404</div>
    <h1 class="error-title">页面未找到</h1>
    <p class="error-desc">抱歉，您访问的页面不存在</p>
    <el-button type="primary" @click="$router.push('/admin')">
      返回首页
    </el-button>
  </div>
</template>

<style scoped>
.error-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #f0f2f5;
}

.error-code {
  font-size: 120px;
  font-weight: bold;
  color: #909399;
}

.error-title {
  font-size: 24px;
  color: #333;
  margin: 20px 0 10px;
}

.error-desc {
  font-size: 16px;
  color: #999;
  margin-bottom: 30px;
}
</style>
