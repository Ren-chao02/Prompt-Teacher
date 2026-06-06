<template>
  <div class="profile-container">
    <!-- 顶部用户卡 -->
    <div class="profile-hero">
      <div class="hero-bg" />
      <div class="hero-content">
        <el-avatar :src="userForm.avatar" :size="96" class="hero-avatar">
          {{ (userForm.username || 'U').charAt(0).toUpperCase() }}
        </el-avatar>
        <div class="hero-info">
          <h2 class="hero-name">
            {{ userForm.username }}
            <el-tag :type="getRoleTagType(userForm.role)" effect="dark" size="small" round>
              {{ getRoleLabel(userForm.role) }}
            </el-tag>
          </h2>
          <p class="hero-bio">{{ userForm.major || '欢迎使用 Prompt Teacher' }}</p>
          <div class="hero-stats">
            <div class="hs-item">
              <div class="hs-num">{{ overview.likes || 0 }}</div>
              <div class="hs-lbl">点赞</div>
            </div>
            <div class="hs-divider" />
            <div class="hs-item">
              <div class="hs-num">{{ overview.favorites || 0 }}</div>
              <div class="hs-lbl">收藏</div>
            </div>
            <div class="hs-divider" />
            <div class="hs-item">
              <div class="hs-num">{{ overview.practices || 0 }}</div>
              <div class="hs-lbl">练习</div>
            </div>
            <div class="hs-divider" />
            <div class="hs-item">
              <div class="hs-num">{{ overview.avg_score || 0 }}</div>
              <div class="hs-lbl">均分</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab 主体 -->
    <el-card shadow="never" class="tab-card">
      <el-tabs v-model="activeTab" class="profile-tabs">
        <!-- Tab 1: 个人信息 -->
        <el-tab-pane name="info" :lazy="false">
          <template #label>
            <span class="tab-label">
              <el-icon><User /></el-icon>个人信息
            </span>
          </template>
          <div class="pane-content">
            <el-form
              ref="formRef"
              :model="userForm"
              :rules="formRules"
              label-width="100px"
            >
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="用户名">
                    <el-input v-model="userForm.username" disabled />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="角色">
                    <el-input :value="getRoleLabel(userForm.role)" disabled />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="邮箱" prop="email">
                    <el-input v-model="userForm.email" placeholder="请输入邮箱" type="email" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="手机号" prop="phone">
                    <el-input v-model="userForm.phone" placeholder="请输入手机号" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="学号" prop="student_id">
                    <el-input
                      v-model="userForm.student_id"
                      placeholder="仅学生角色需要"
                      :disabled="userForm.role !== 'student'"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="专业" prop="major">
                    <el-input v-model="userForm.major" placeholder="请输入专业" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="学期" prop="semester">
                    <el-input v-model="userForm.semester" placeholder="格式: 2024-2025-1" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="注册时间">
                    <el-input :value="formatDate(userForm.date_joined)" disabled />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-form-item>
                <el-button type="primary" :loading="saveLoading" @click="handleSaveProfile">
                  保存修改
                </el-button>
                <el-button @click="resetForm">重置</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- Tab 2: 安全设置 -->
        <el-tab-pane name="security" :lazy="false">
          <template #label>
            <span class="tab-label">
              <el-icon><Lock /></el-icon>安全设置
            </span>
          </template>
          <div class="pane-content">
            <el-form
              ref="passwordFormRef"
              :model="passwordForm"
              :rules="passwordRules"
              label-width="100px"
              style="max-width: 540px;"
            >
              <el-form-item label="当前密码" prop="old_password">
                <el-input
                  v-model="passwordForm.old_password"
                  type="password"
                  show-password
                  placeholder="请输入当前密码"
                />
              </el-form-item>
              <el-form-item label="新密码" prop="new_password">
                <el-input
                  v-model="passwordForm.new_password"
                  type="password"
                  show-password
                  placeholder="请输入新密码（至少6位）"
                />
              </el-form-item>
              <el-form-item label="确认新密码" prop="new_password_confirm">
                <el-input
                  v-model="passwordForm.new_password_confirm"
                  type="password"
                  show-password
                  placeholder="请再次输入新密码"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="warning" :loading="passwordLoading" @click="handleChangePassword">
                  修改密码
                </el-button>
                <el-button @click="resetPassword">重置</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- Tab 3: 我的收藏 -->
        <el-tab-pane name="favorites" :lazy="false">
          <template #label>
            <span class="tab-label">
              <el-icon><CollectionTag /></el-icon>我的收藏
              <el-badge v-if="favorites.length" :value="favorites.length" class="tab-badge" />
            </span>
          </template>
          <div class="pane-content" v-loading="loadingFav">
            <el-empty v-if="!favorites.length" description="还没有收藏任何内容" />
            <div v-else class="fav-grid">
              <div
                v-for="item in favorites"
                :key="item.id"
                class="fav-item"
                @click="goDetail(item)"
              >
                <div class="fav-cover" :style="getCoverStyle(item)">
                  <el-icon><Document /></el-icon>
                </div>
                <div class="fav-body">
                  <h4 class="fav-title">{{ item.title }}</h4>
                  <p class="fav-summary">{{ item.summary || '暂无摘要' }}</p>
                  <div class="fav-meta">
                    <span><el-icon><View /></el-icon>{{ item.view_count || 0 }}</span>
                    <span><el-icon><Star /></el-icon>{{ item.like_count || 0 }}</span>
                    <span class="fav-time">{{ formatDate(item.favorited_at || item.updated_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- Tab 4: 练习记录 -->
        <el-tab-pane name="practices" :lazy="false">
          <template #label>
            <span class="tab-label">
              <el-icon><EditPen /></el-icon>练习记录
            </span>
          </template>
          <div class="pane-content" v-loading="loadingPrac">
            <el-empty v-if="!practices.length" description="暂无练习记录" />
            <el-table v-else :data="practices" stripe>
              <el-table-column prop="scenario_title" label="场景" />
              <el-table-column label="得分" width="120" align="center">
                <template #default="{ row }">
                  <el-tag :type="getScoreType(row.score)">{{ row.score }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="用时" width="100" align="center">
                <template #default="{ row }">{{ row.duration || '-' }}</template>
              </el-table-column>
              <el-table-column label="提交时间" width="180">
                <template #default="{ row }">{{ formatDate(row.submitted_at) }}</template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- Tab 5: 活动日志 -->
        <el-tab-pane name="activities" :lazy="false">
          <template #label>
            <span class="tab-label">
              <el-icon><Clock /></el-icon>活动日志
            </span>
          </template>
          <div class="pane-content" v-loading="loadingAct">
            <el-timeline v-if="activities.length">
              <el-timeline-item
                v-for="(act, i) in activities"
                :key="i"
                :timestamp="formatDate(act.created_at)"
                :type="getActColor(act.type)"
                placement="top"
              >
                <div class="act-item">
                  <div class="act-title">{{ act.title }}</div>
                  <div class="act-desc">{{ act.description }}</div>
                </div>
              </el-timeline-item>
            </el-timeline>
            <el-empty v-else description="暂无活动记录" />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User,
  Lock,
  CollectionTag,
  EditPen,
  Clock,
  Document,
  View,
  Star
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/modules/auth'
import { getUserInfoApi, changePasswordApi } from '@/api/auth'
import { getMyFavorites } from '@/api/learning'
import { getUserStatistics } from '@/api/user'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref(localStorage.getItem('profileTab') || 'info')
watch(activeTab, (v) => localStorage.setItem('profileTab', v))

const formRef = ref(null)
const passwordFormRef = ref(null)
const saveLoading = ref(false)
const passwordLoading = ref(false)

const loadingFav = ref(false)
const loadingPrac = ref(false)
const loadingAct = ref(false)

const userForm = reactive({
  username: '',
  email: '',
  phone: '',
  avatar: '',
  role: '',
  student_id: '',
  major: '',
  semester: '',
  date_joined: '',
  last_login: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  new_password_confirm: ''
})

const favorites = ref([])
const practices = ref([])
const activities = ref([])
const overview = ref({ likes: 0, favorites: 0, practices: 0, avg_score: 0 })

const formRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

const validatePasswordConfirm = (rule, value, callback) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的新密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  old_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 128, message: '密码长度在 6 到 128 个字符', trigger: 'blur' }
  ],
  new_password_confirm: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validatePasswordConfirm, trigger: 'blur' }
  ]
}

onMounted(async () => {
  await fetchUserInfo()
  fetchStatistics()
  if (activeTab.value === 'favorites') fetchFavorites()
})

watch(activeTab, (v) => {
  if (v === 'favorites' && !favorites.value.length) fetchFavorites()
  if (v === 'practices' && !practices.value.length) fetchPractices()
  if (v === 'activities' && !activities.value.length) fetchActivities()
})

async function fetchUserInfo() {
  try {
    const res = await getUserInfoApi()
    const u = res.data
    Object.assign(userForm, {
      username: u.username || '',
      email: u.email || '',
      phone: u.phone || '',
      avatar: u.avatar || '',
      role: u.role || '',
      student_id: u.student_id || '',
      major: u.major || '',
      semester: u.semester || '',
      date_joined: u.date_joined || '',
      last_login: u.last_login || ''
    })
    authStore.user = u
  } catch (e) {
    console.error(e)
  }
}

async function fetchStatistics() {
  try {
    const res = await getUserStatistics()
    const d = res.data.data || res.data
    overview.value = d || overview.value
  } catch (e) {
    /* 静默 */
  }
}

async function fetchFavorites() {
  loadingFav.value = true
  try {
    const res = await getMyFavorites({ page: 1, page_size: 12 })
    const d = res.data.data || res.data
    favorites.value = d.results || d || []
  } catch (e) {
    ElMessage.error('加载收藏失败')
  } finally {
    loadingFav.value = false
  }
}

async function fetchPractices() {
  loadingPrac.value = true
  try {
    const res = await fetch('/api/v1/practice/submissions/?page=1&page_size=20', {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    if (res.ok) {
      const j = await res.json()
      const d = j.data || j
      practices.value = d.results || d || []
    }
  } catch (e) {
    practices.value = []
  } finally {
    loadingPrac.value = false
  }
}

async function fetchActivities() {
  loadingAct.value = true
  try {
    const res = await fetch('/api/v1/users/activities/?page=1&page_size=20', {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    if (res.ok) {
      const j = await res.json()
      const d = j.data || j
      activities.value = d.results || d || []
    }
  } catch (e) {
    activities.value = []
  } finally {
    loadingAct.value = false
  }
}

async function handleSaveProfile() {
  await nextTick()
  const form = formRef.value
  if (!form || typeof form.validate !== 'function') {
    ElMessage.warning('请先切换到"个人信息"标签页')
    return
  }
  const valid = await form.validate().catch(() => false)
  if (!valid) return

  saveLoading.value = true
  try {
    const updateData = {
      email: userForm.email,
      phone: userForm.phone,
      student_id: userForm.student_id,
      major: userForm.major,
      semester: userForm.semester
    }
    const res = await fetch('/api/v1/auth/me/', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.token}`
      },
      body: JSON.stringify(updateData)
    })
    if (res.ok) {
      ElMessage.success('个人信息更新成功')
      await fetchUserInfo()
    } else {
      throw new Error('更新失败')
    }
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saveLoading.value = false
  }
}

async function handleChangePassword() {
  await nextTick()
  const form = passwordFormRef.value
  if (!form || typeof form.validate !== 'function') {
    ElMessage.warning('请先切换到"安全设置"标签页')
    return
  }
  const valid = await form.validate().catch(() => false)
  if (!valid) return

  try {
    await ElMessageBox.confirm(
      '确定要修改密码吗？修改后需要重新登录！',
      '提示',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    passwordLoading.value = true
    await changePasswordApi(passwordForm)
    ElMessage.success('密码修改成功，即将跳转登录页...')
    setTimeout(() => {
      authStore.logout()
      window.location.href = '/admin/login/'
    }, 1500)
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  } finally {
    passwordLoading.value = false
  }
}

function resetForm() {
  fetchUserInfo()
}

function resetPassword() {
  Object.assign(passwordForm, {
    old_password: '',
    new_password: '',
    new_password_confirm: ''
  })
  if (passwordFormRef.value) passwordFormRef.value.clearValidate()
}

function goDetail(item) {
  router.push(`/learning/detail/${item.id}`)
}

function getRoleLabel(r) {
  return { admin: '管理员', teacher: '教师', student: '学生' }[r] || r
}
function getRoleTagType(r) {
  return { admin: 'danger', teacher: 'warning', student: 'success' }[r] || 'info'
}
function getCoverStyle(item) {
  const map = {
    basic: 'linear-gradient(135deg, #3B82F6, #60A5FA)',
    intermediate: 'linear-gradient(135deg, #F59E0B, #FBBF24)',
    advanced: 'linear-gradient(135deg, #EF4444, #F87171)',
    best_practices: 'linear-gradient(135deg, #10B981, #6EE7B7)'
  }
  return { background: map[item.category] || map.basic }
}
function getScoreType(s) {
  if (s >= 80) return 'success'
  if (s >= 60) return 'warning'
  return 'danger'
}
function getActColor(t) {
  return { like: 'danger', favorite: 'warning', practice: 'success', view: 'primary' }[t] || 'info'
}
function formatDate(s) {
  if (!s) return '-'
  return new Date(s).toLocaleString('zh-CN', { hour12: false })
}
</script>

<style scoped>
.profile-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Hero */
.profile-hero {
  position: relative;
  border-radius: 18px;
  overflow: hidden;
  background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%);
  color: #ffffff;
  box-shadow: 0 12px 40px rgba(79, 70, 229, 0.25);
}

.hero-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 20%, rgba(255,255,255,0.18) 0%, transparent 40%),
    radial-gradient(circle at 80% 80%, rgba(255,255,255,0.12) 0%, transparent 40%);
  pointer-events: none;
}

.hero-content {
  position: relative;
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 32px 36px;
}

.hero-avatar {
  background: rgba(255,255,255,0.2);
  color: #ffffff;
  font-size: 36px;
  font-weight: 700;
  border: 4px solid rgba(255,255,255,0.3);
  backdrop-filter: blur(8px);
}

.hero-info {
  flex: 1;
}

.hero-name {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 4px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.hero-bio {
  font-size: 14px;
  opacity: 0.9;
  margin: 0 0 16px;
}

.hero-stats {
  display: flex;
  align-items: center;
  gap: 18px;
  background: rgba(255,255,255,0.15);
  padding: 12px 24px;
  border-radius: 12px;
  backdrop-filter: blur(8px);
  width: fit-content;
}

.hs-item {
  text-align: center;
}

.hs-num {
  font-size: 20px;
  font-weight: 700;
  line-height: 1.2;
}

.hs-lbl {
  font-size: 12px;
  opacity: 0.9;
}

.hs-divider {
  width: 1px;
  height: 28px;
  background: rgba(255,255,255,0.3);
}

/* Tabs */
.tab-card {
  border-radius: 14px;
}

.profile-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
  padding: 0 16px;
  background: #FAFAFA;
  border-radius: 14px 14px 0 0;
}

.profile-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background: #E5E7EB;
}

.tab-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.tab-badge {
  margin-left: 4px;
}

.pane-content {
  padding: 24px 12px;
  min-height: 360px;
}

/* Favorites */
.fav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.fav-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #FAFAFA;
  border: 1px solid #F3F4F6;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.fav-item:hover {
  background: #ffffff;
  border-color: #DBEAFE;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.08);
  transform: translateY(-2px);
}

.fav-cover {
  width: 56px;
  height: 56px;
  flex-shrink: 0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 24px;
}

.fav-body {
  flex: 1;
  min-width: 0;
}

.fav-title {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.fav-summary {
  font-size: 12px;
  color: #6B7280;
  margin: 0 0 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.fav-meta {
  display: flex;
  gap: 10px;
  font-size: 11px;
  color: #9CA3AF;
}

.fav-meta span {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.fav-time {
  margin-left: auto;
}

/* Activities */
.act-item {
  background: #FAFAFA;
  padding: 12px 16px;
  border-radius: 8px;
  border-left: 3px solid #6366F1;
}

.act-title {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 2px;
}

.act-desc {
  font-size: 12px;
  color: #6B7280;
}

@media (max-width: 768px) {
  .hero-content { flex-direction: column; text-align: center; }
  .hero-stats { width: 100%; justify-content: space-around; }
}
</style>
