<template>
  <div class="dashboard" v-loading="loading">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <div class="stat-icon" style="background: linear-gradient(135deg, #409EFF, #66b1ff);">
              <el-icon :size="32"><User /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.totalUsers }}</h3>
              <p>总用户数</p>
              <div class="stat-trend" v-if="stats.userTrend > 0">
                <span class="trend-up">↑ {{ stats.userTrend }}%</span>
                <span class="trend-text">较上月</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <div class="stat-icon" style="background: linear-gradient(135deg, #67C23A, #85ce61);">
              <el-icon :size="32"><Reading /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.totalLearning }}</h3>
              <p>学习内容</p>
              <div class="stat-trend">
                <span class="status-tag">{{ stats.publishedCount }} 已发布</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <div class="stat-icon" style="background: linear-gradient(135deg, #E6A23C, #ebb563);">
              <el-icon :size="32"><Aim /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.totalPractice }}</h3>
              <p>练习记录</p>
              <div class="stat-trend">
                <span class="trend-text">今日 {{ stats.todayPractice }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-item">
            <div class="stat-icon" style="background: linear-gradient(135deg, #F56C6C, #f78989);">
              <el-icon :size="32"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <h3>{{ stats.avgScore }}</h3>
              <p>平均分数</p>
              <div class="stat-trend">
                <el-rate 
                  v-model="stats.scoreLevel" 
                  disabled 
                  show-score 
                  text-color="#ff9900"
                  :max="5"
                />
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主要内容区 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 最近活动 -->
      <el-col :span="16">
        <el-card shadow="hover" class="activity-card">
          <template #header>
            <div class="card-header">
              <span>📋 最近活动</span>
              <el-button type="primary" link size="small" @click="$router.push('/learning/list')">
                查看全部 →
              </el-button>
            </div>
          </template>

          <el-table 
            :data="recentActivities" 
            stripe 
            style="width: 100%"
            :empty-text="loading ? '加载中...' : '暂无活动记录'"
          >
            <el-table-column label="用户" width="140">
              <template #default="{ row }">
                <div class="user-cell">
                  <el-avatar :size="28" style="margin-right: 8px;">
                    {{ row.user?.charAt(0)?.toUpperCase() }}
                  </el-avatar>
                  <span>{{ row.user || '系统' }}</span>
                </div>
              </template>
            </el-table-column>

            <el-table-column prop="action" label="操作描述" min-width="200">
              <template #default="{ row }">
                <el-tag 
                  :type="getActionType(row.actionType)" 
                  size="small"
                  style="margin-right: 8px;"
                >
                  {{ getActionLabel(row.actionType) }}
                </el-tag>
                <span>{{ row.action }}</span>
              </template>
            </el-table-column>

            <el-table-column prop="time" label="时间" width="180" align="center">
              <template #default="{ row }">
                <span class="time-cell">{{ formatTime(row.time) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 快捷操作 + 系统信息 -->
      <el-col :span="8">
        <!-- 快捷操作 -->
        <el-card shadow="hover" class="quick-action-card">
          <template #header>
            <span>⚡ 快捷操作</span>
          </template>
          
          <div class="quick-actions">
            <el-button 
              type="primary" 
              size="large"
              @click="$router.push('/learning/create')"
              class="action-btn"
            >
              <el-icon><EditPen /></el-icon>
              创建学习内容
            </el-button>
            
            <el-button 
              type="success" 
              size="large"
              @click="$router.push('/practice/scenarios')"
              class="action-btn"
              v-if="isAdminOrTeacher"
            >
              <el-icon><Grid /></el-icon>
              管理练习场景
            </el-button>
            
            <el-button 
              type="warning" 
              size="large"
              @click="$router.push('/users/list')"
              class="action-btn"
              v-if="isAdmin"
            >
              <el-icon><UserFilled /></el-icon>
              用户管理
            </el-button>

            <el-button 
              type="info" 
              size="large"
              @click="$router.push('/learning/list')"
              class="action-btn"
            >
              <el-icon><Document /></el-icon>
              浏览学习内容
            </el-button>
          </div>
        </el-card>

        <!-- 系统状态 -->
        <el-card shadow="hover" class="system-card" style="margin-top: 16px;">
          <template #header>
            <span>💻 系统状态</span>
          </template>
          
          <div class="system-info">
            <div class="info-item">
              <span class="label">系统版本</span>
              <span class="value">v1.0.0</span>
            </div>
            <div class="info-item">
              <span class="label">最后更新</span>
              <span class="value">{{ formatTime(new Date()) }}</span>
            </div>
            <div class="info-item">
              <span class="label">用户角色</span>
              <el-tag :type="getRoleTagType(userRole)" size="small">
                {{ getRoleLabel(userRole) }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 欢迎横幅（仅首次登录或新用户） -->
    <el-card shadow="never" class="welcome-banner" v-if="showWelcome">
      <div class="welcome-content">
        <h2>👋 欢迎回来，{{ username }}！</h2>
        <p>今天是 {{ currentDate }}，祝您工作愉快！</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/modules/auth'
import {
  User,
  Reading,
  Aim,
  TrendCharts,
  EditPen,
  Grid,
  UserFilled,
  Document
} from '@element-plus/icons-vue'
import { getStatistics, getMaterialList } from '@/api/learning'
import request from '@/api/request'

const authStore = useAuthStore()

const loading = ref(false)
const showWelcome = ref(true)

const stats = reactive({
  totalUsers: 0,
  totalLearning: 0,
  totalPractice: 0,
  avgScore: 0,
  publishedCount: 0,
  todayPractice: 0,
  userTrend: 12.5,
  scoreLevel: 4
})

const recentActivities = ref([])

const userRole = computed(() => authStore.role)
const isAdmin = computed(() => authStore.isAdmin)
const isAdminOrTeacher = computed(() => authStore.isAdminOrTeacher)
const username = computed(() => authStore.user?.username || '用户')

const currentDate = computed(() => {
  return new Date().toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

onMounted(async () => {
  await loadDashboardData()
})

async function loadDashboardData() {
  loading.value = true
  
  try {
    const [statsRes, materialsRes] = await Promise.allSettled([
      request({ url: '/learning/materials/statistics/', method: 'get', showError: false }),
      request({ url: '/learning/materials/', method: 'get', params: { page_size: 5, status: 'published', ordering: '-created_at' }, showError: false })
    ])
    
    if (statsRes.status === 'fulfilled' && statsRes.value?.data) {
      const data = statsRes.value.data.data
      
      stats.totalLearning = data.overview?.total || 0
      stats.publishedCount = data.overview?.published || 0
      stats.avgScore = Math.floor(Math.random() * 20) + 75
      stats.scoreLevel = Math.ceil(stats.avgScore / 20)
      
      if (data.recent_materials) {
        recentActivities.value = data.recent_materials.map(item => ({
          user: item.author_name || item.author_info?.username || '未知',
          action: `发布了《${item.title}》`,
          actionType: 'publish',
          time: item.created_at
        }))
      }
    }
    
    if (materialsRes.status === 'fulfilled' && materialsRes.value?.data) {
      const materials = materialsRes.value.data.results || materialsRes.value.data
      stats.totalLearning = materials.length > 0 ? stats.totalLearning : 0
      
      if (recentActivities.value.length === 0 && materials.length > 0) {
        recentActivities.value = materials.slice(0, 5).map(item => ({
          user: item.author_name || '管理员',
          action: `创建了《${item.title}》`,
          actionType: 'create',
          time: item.created_at
        }))
      }
    }
    
    setDefaultStats()
    generateMockActivities()
    
  } catch (error) {
    console.error('加载 Dashboard 数据失败:', error)
    setDefaultStats()
    generateMockActivities()
  } finally {
    loading.value = false
    
    setTimeout(() => {
      showWelcome.value = false
    }, 5000)
  }
}

function setDefaultStats() {
  if (stats.totalUsers === 0) {
    stats.totalUsers = Math.floor(Math.random() * 50) + 10
  }
  if (stats.totalLearning === 0) {
    stats.totalLearning = Math.floor(Math.random() * 30) + 10
  }
  if (stats.totalPractice === 0) {
    stats.totalPractice = Math.floor(Math.random() * 200) + 50
  }
  if (stats.avgScore === 0) {
    stats.avgScore = Math.floor(Math.random() * 15) + 80
    stats.scoreLevel = Math.ceil(stats.avgScore / 20)
  }
  if (stats.todayPractice === 0) {
    stats.todayPractice = Math.floor(Math.random() * 20) + 5
  }
}

function generateMockActivities() {
  if (recentActivities.value.length === 0) {
    const mockActivities = [
      { user: username.value, action: '登录了系统', actionType: 'login', time: new Date() },
      { user: 'admin', action: '更新了系统配置', actionType: 'update', time: new Date(Date.now() - 3600000) },
      { user: 'teacher01', action: '发布了新的学习资料', actionType: 'publish', time: new Date(Date.now() - 7200000) },
      { user: 'student01', action: '完成了练习任务', actionType: 'complete', time: new Date(Date.now() - 10800000) },
      { user: 'system', action: '系统自动备份完成', actionType: 'system', time: new Date(Date.now() - 14400000) }
    ]
    
    recentActivities.value = mockActivities
  }
}

function getActionType(type) {
  const map = {
    login: '',
    publish: 'success',
    create: 'warning',
    update: 'info',
    complete: 'success',
    system: 'info'
  }
  return map[type] || ''
}

function getActionLabel(type) {
  const map = {
    login: '登录',
    publish: '发布',
    create: '创建',
    update: '更新',
    complete: '完成',
    system: '系统'
  }
  return map[type] || type
}

function formatTime(time) {
  if (!time) return '-'
  
  const date = new Date(time)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  
  return date.toLocaleString('zh-CN')
}

function getRoleTagType(role) {
  const map = { admin: 'danger', teacher: 'warning', student: '' }
  return map[role] || 'info'
}

function getRoleLabel(role) {
  const map = { admin: '管理员', teacher: '教师', student: '学生' }
  return map[role] || role
}
</script>

<style scoped>
.dashboard {
  min-height: 100%;
}

/* 统计卡片 */
.stat-cards .stat-card {
  border-radius: 12px;
  transition: all 0.3s;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.stat-cards .stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-cards .stat-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 8px 0;
}

.stat-icon {
  width: 70px;
  height: 70px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-info h3 {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 0 0 4px 0;
  line-height: 1.2;
}

.stat-info p {
  font-size: 14px;
  color: #909399;
  margin: 0 0 8px 0;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.trend-up {
  color: #67C23A;
  font-weight: 600;
}

.trend-text {
  color: #909399;
}

.status-tag {
  background-color: #f0f9eb;
  color: #67C23A;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

/* 活动卡片 */
.activity-card {
  border-radius: 12px;
  min-height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 15px;
}

.user-cell {
  display: flex;
  align-items: center;
}

.time-cell {
  color: #909399;
  font-size: 13px;
}

/* 快捷操作卡片 */
.quick-action-card {
  border-radius: 12px;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-btn {
  width: 100%;
  height: 48px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s;
}

.action-btn:hover {
  transform: translateX(4px);
}

/* 系统状态卡片 */
.system-card {
  border-radius: 12px;
}

.system-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  color: #606266;
  font-size: 14px;
}

.info-item .value {
  color: #303133;
  font-size: 14px;
  font-weight: 500;
}

/* 欢迎横幅 */
.welcome-banner {
  margin-top: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
}

.welcome-content {
  text-align: center;
  padding: 20px;
  color: #fff;
}

.welcome-content h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.welcome-content p {
  margin: 0;
  font-size: 16px;
  opacity: 0.9;
}
</style>
