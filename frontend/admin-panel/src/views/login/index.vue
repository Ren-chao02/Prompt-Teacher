<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1 class="title">Prompt Teacher</h1>
        <p class="subtitle">智能教学管理平台</p>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs" stretch>
        <!-- 学生登录 -->
        <el-tab-pane name="student">
          <template #label>
            <span class="tab-label"><el-icon><User /></el-icon>学生登录</span>
          </template>
          <el-form ref="formRef" :model="form" :rules="studentRules" @keyup.enter="handleLogin">
            <el-form-item prop="identifier">
              <el-input v-model="form.identifier" placeholder="请输入学号" size="large"
                prefix-icon="Postcard" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="form.password" type="password" placeholder="请输入密码"
                size="large" prefix-icon="Lock" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" size="large" :loading="loading"
                class="login-button" @click="handleLogin">{{ loading ? '登录中...' : '登 录' }}</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 教师登录 -->
        <el-tab-pane name="teacher">
          <template #label>
            <span class="tab-label"><el-icon><Briefcase /></el-icon>教师登录</span>
          </template>
          <el-form ref="formRef" :model="form" :rules="teacherRules" @keyup.enter="handleLogin">
            <el-form-item prop="identifier">
              <el-input v-model="form.identifier" placeholder="请输入工号" size="large"
                prefix-icon="Ticket" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="form.password" type="password" placeholder="请输入密码"
                size="large" prefix-icon="Lock" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" size="large" :loading="loading"
                class="login-button" @click="handleLogin">{{ loading ? '登录中...' : '登 录' }}</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 管理员登录 -->
        <el-tab-pane name="admin">
          <template #label>
            <span class="tab-label"><el-icon><Setting /></el-icon>管理员</span>
          </template>
          <el-form ref="formRef" :model="form" :rules="adminRules" @keyup.enter="handleLogin">
            <el-form-item prop="identifier">
              <el-input v-model="form.identifier" placeholder="请输入用户名" size="large"
                prefix-icon="User" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="form.password" type="password" placeholder="请输入密码"
                size="large" prefix-icon="Lock" show-password />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" size="large" :loading="loading"
                class="login-button" @click="handleLogin">{{ loading ? '登录中...' : '登 录' }}</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 首次登录密码修改提醒 -->
    <el-dialog v-model="showPwdDialog" title="安全提示" width="420px"
      :close-on-click-modal="false" :show-close="false" append-to-body>
      <el-alert type="warning" :closable="false" show-icon style="margin-bottom:16px">
        <template #title>检测到您是首次登录</template>
        <p style="margin:4px 0 0;font-size:13px">您的默认密码为手机号后6位，为了账号安全，请尽快修改密码。</p>
      </el-alert>
      <p style="color:#666;font-size:13px;margin-bottom:16px">
        您可以在登录后进入「个人中心 → 安全设置」中修改密码。
      </p>
      <template #footer>
        <el-button type="primary" @click="handlePwdConfirm">我知道了，稍后修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Briefcase, Setting } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/modules/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const activeTab = ref('student')
const formRef = ref(null)
const loading = ref(false)
const showPwdDialog = ref(false)

const form = reactive({ identifier: '', password: '' })

const requiredRule = (msg) => ({ required: true, message: msg, trigger: 'blur' })
const pwdRule = { required: true, message: '请输入密码', trigger: 'blur' }

const studentRules = {
  identifier: [requiredRule('请输入学号')],
  password: pwdRule
}
const teacherRules = {
  identifier: [requiredRule('请输入工号')],
  password: pwdRule
}
const adminRules = {
  identifier: [requiredRule('请输入用户名')],
  password: pwdRule
}

async function handleLogin() {
  if (!formRef.value) return
  try { await formRef.value.validate() } catch (_e) { return }

  loading.value = true
  try {
    await authStore.login({
      identifier: form.identifier,
      password: form.password,
      // 前端 tab 名 → 后端认证字段名映射
      login_type: activeTab.value === 'student' ? 'student_id'
        : (activeTab.value === 'teacher' ? 'employee_id'
        : 'username')
    })
    ElMessage.success('登录成功')
    // 首次登录/需修改密码时弹窗提醒
    if (authStore.mustChangePassword) {
      showPwdDialog.value = true
    } else {
      router.push(route.query.redirect || '/dashboard')
    }
  } catch (e) {
    console.error(e)
    // 改进登录错误提示
    const errMsg = e?.response?.data?.detail || e?.message || e?.toString() || ''
    if (errMsg.includes('账号或密码') || e?.response?.status === 400 || e?.response?.status === 401) {
      const pwdHint = activeTab.value === 'teacher'
        ? '\n提示：教师默认密码为手机号后6位'
        : activeTab.value === 'student'
        ? '\n提示：学生默认密码为手机号后6位或123456'
        : ''
      ElMessage.error(`账号或密码错误${pwdHint}`)
    } else {
      ElMessage.error(errMsg || '登录失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

function handlePwdConfirm() {
  showPwdDialog.value = false
  router.push(route.query.redirect || '/dashboard')
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 420px;
  padding: 36px 40px 32px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, .25);
}

.login-header {
  text-align: center;
  margin-bottom: 24px;
}

.title {
  font-size: 26px;
  font-weight: 700;
  color: #333;
  margin: 0 0 6px;
}

.subtitle {
  font-size: 14px;
  color: #999;
  margin: 0;
}

.login-button {
  width: 100%;
  height: 46px;
  font-size: 16px;
  border-radius: 8px;
}

.tab-label {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
}

.login-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
}

.login-tabs :deep(.el-tabs__item) {
  height: 44px;
  line-height: 44px;
  font-size: 14px;
}
</style>
