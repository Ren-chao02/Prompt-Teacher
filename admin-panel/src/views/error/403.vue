<template>
  <div class="error-page">
    <div class="error-code">403</div>
    <h1 class="error-title">访问被拒绝</h1>
    <p class="error-desc">抱歉，您没有权限访问此页面</p>
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
  color: #F56C6C;
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
