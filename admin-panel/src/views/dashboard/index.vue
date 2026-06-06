<template>
  <div class="dashboard" v-loading="loading">
    <!-- 错误提示 -->
    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      show-icon
      closable
      @close="errorMessage = ''"
      style="margin-bottom: 20px;"
    />

    <!-- 顶部欢迎横幅 -->
    <div class="welcome-banner" v-if="showWelcome">
      <div class="welcome-content">
        <div class="welcome-left">
          <h1 class="welcome-title">{{ greetingText }}，{{ username }}！</h1>
          <p class="welcome-subtitle">{{ currentDate }} · {{ getRoleLabel(userRole) }}</p>
          <p class="welcome-tip">{{ roleBasedTip }}</p>
        </div>
        <div class="welcome-illustration">
          <el-icon :size="100" class="welcome-icon"><Sunny /></el-icon>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :xs="12" :sm="12" :md="6">
        <div class="stat-card stat-card--blue">
          <div class="stat-icon">
            <el-icon :size="28"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalUsers }}</div>
            <div class="stat-label">总用户数</div>
            <div class="stat-trend" v-if="isAdmin">
              <span class="trend-up">↑ {{ stats.userTrend }}%</span>
              <span class="trend-text">较上月</span>
            </div>
          </div>
        </div>
      </el-col>

      <el-col :xs="12" :sm="12" :md="6">
        <div class="stat-card stat-card--green">
          <div class="stat-icon">
            <el-icon :size="28"><Reading /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalLearning }}</div>
            <div class="stat-label">学习内容</div>
            <div class="stat-trend">
              <span class="trend-text">{{ stats.publishedCount }} 已发布</span>
            </div>
          </div>
        </div>
      </el-col>

      <el-col :xs="12" :sm="12" :md="6">
        <div class="stat-card stat-card--orange">
          <div class="stat-icon">
            <el-icon :size="28"><Aim /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalPractice }}</div>
            <div class="stat-label">练习记录</div>
            <div class="stat-trend">
              <span class="trend-text">今日 {{ stats.todayPractice }}</span>
            </div>
          </div>
        </div>
      </el-col>

      <el-col :xs="12" :sm="12" :md="6">
        <div class="stat-card stat-card--red">
          <div class="stat-icon">
            <el-icon :size="28"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.avgScore }}</div>
            <div class="stat-label">平均分数</div>
            <div class="stat-trend">
              <el-rate
                v-model="stats.scoreLevel"
                disabled
                :max="5"
                size="small"
              />
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 学习进度 + 最近活动 -->
    <el-row :gutter="20" style="margin-top: 8px;">
      <!-- 学习进度卡片 -->
      <el-col :xs="24" :lg="12">
        <div class="content-card progress-card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><DataLine /></el-icon>
              <span>学习进度</span>
            </div>
            <el-button type="primary" link @click="$router.push('/analytics/learning')">
              查看详情 →
            </el-button>
          </div>

          <div class="progress-content">
            <div class="progress-main">
              <div class="progress-ring">
                <el-progress
                  type="circle"
                  :percentage="progressData.weeklyPercent"
                  :stroke-width="10"
                  :width="140"
                  :color="progressColors"
                />
              </div>
              <div class="progress-info">
                <div class="info-item">
                  <span class="info-label">本周完成</span>
                  <span class="info-value">{{ progressData.weeklyCompleted }} 篇</span>
                </div>
                <div class="info-item">
                  <span class="info-label">待学内容</span>
                  <span class="info-value pending">{{ progressData.pending }} 篇</span>
                </div>
                <div class="info-item">
                  <span class="info-label">连续学习</span>
                  <span class="info-value streak">🔥 {{ progressData.streak }} 天</span>
                </div>
              </div>
            </div>

            <div class="progress-bar-section">
              <div class="bar-row">
                <span class="bar-label">入门</span>
                <div class="bar-track">
                  <div class="bar-fill" :style="{ width: progressData.beginner + '%', background: 'linear-gradient(90deg, #10B981, #34D399)' }"></div>
                </div>
                <span class="bar-value">{{ progressData.beginner }}%</span>
              </div>
              <div class="bar-row">
                <span class="bar-label">进阶</span>
                <div class="bar-track">
                  <div class="bar-fill" :style="{ width: progressData.intermediate + '%', background: 'linear-gradient(90deg, #3B82F6, #60A5FA)' }"></div>
                </div>
                <span class="bar-value">{{ progressData.intermediate }}%</span>
              </div>
              <div class="bar-row">
                <span class="bar-label">高级</span>
                <div class="bar-track">
                  <div class="bar-fill" :style="{ width: progressData.advanced + '%', background: 'linear-gradient(90deg, #F59E0B, #FBBF24)' }"></div>
                </div>
                <span class="bar-value">{{ progressData.advanced }}%</span>
              </div>
            </div>
          </div>
        </div>
      </el-col>

      <!-- 最近活动 -->
      <el-col :xs="24" :lg="12">
        <div class="content-card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Bell /></el-icon>
              <span>最近活动</span>
            </div>
            <el-button type="primary" link @click="$router.push('/practice/records')">
              更多 →
            </el-button>
          </div>

          <div class="activity-list" v-loading="loading">
            <transition-group name="activity-fade" tag="div">
              <div
                v-for="(activity, idx) in recentActivities"
                :key="activity.id || idx"
                class="activity-item"
              >
                <div class="activity-icon" :class="`activity-icon--${activity.actionType}`">
                  <el-icon :size="18">
                    <component :is="activity.iconComponent" />
                  </el-icon>
                </div>
                <div class="activity-body">
                  <div class="activity-desc">
                    <span class="activity-user">{{ activity.user }}</span>
                    <span class="activity-text">{{ activity.action }}</span>
                  </div>
                  <div class="activity-time">{{ formatTime(activity.time) }}</div>
                </div>
              </div>

              <div v-if="!loading && recentActivities.length === 0" class="activity-empty">
                <el-icon :size="48" color="#D1D5DB"><DocumentRemove /></el-icon>
                <p>暂无活动记录</p>
              </div>
            </transition-group>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :xs="24" :lg="12">
        <div class="content-card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><PieChart /></el-icon>
              <span>学习内容分类</span>
            </div>
            <el-tag size="small" type="info" effect="plain">共 {{ categoryChartData.total }} 篇</el-tag>
          </div>
          <BaseChart
            :option="categoryChartOption"
            height="320px"
            @click="handleCategoryClick"
          />
        </div>
      </el-col>

      <el-col :xs="24" :lg="12">
        <div class="content-card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><DataAnalysis /></el-icon>
              <span>练习成绩趋势</span>
            </div>
            <div class="chart-tabs">
              <span
                v-for="tab in trendTabs"
                :key="tab.value"
                class="tab-item"
                :class="{ active: trendRange === tab.value }"
                @click="trendRange = tab.value"
              >{{ tab.label }}</span>
            </div>
          </div>
          <BaseChart
            :option="scoreTrendOption"
            height="320px"
          />
        </div>
      </el-col>
    </el-row>

    <!-- 快捷操作 + 系统信息 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :xs="24" :lg="16">
        <div class="content-card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Lightning /></el-icon>
              <span>快捷操作</span>
            </div>
          </div>
          <div class="quick-actions">
            <el-button
              type="primary"
              @click="$router.push('/learning/create')"
              class="action-btn"
              v-if="isAdminOrTeacher"
            >
              <el-icon><EditPen /></el-icon>
              <span>创建学习内容</span>
            </el-button>
            <el-button
              type="success"
              @click="$router.push('/practice/scenarios')"
              class="action-btn"
              v-if="isAdminOrTeacher"
            >
              <el-icon><Grid /></el-icon>
              <span>管理练习场景</span>
            </el-button>
            <el-button
              type="warning"
              @click="$router.push('/learning/my')"
              class="action-btn"
              v-if="isAdminOrTeacher"
            >
              <el-icon><Document /></el-icon>
              <span>我的内容</span>
            </el-button>
            <el-button
              type="info"
              @click="$router.push('/users/list')"
              class="action-btn"
              v-if="isAdmin"
            >
              <el-icon><UserFilled /></el-icon>
              <span>用户管理</span>
            </el-button>
            <el-button
              @click="$router.push('/learning/list')"
              class="action-btn"
            >
              <el-icon><Reading /></el-icon>
              <span>浏览学习内容</span>
            </el-button>
            <el-button
              @click="$router.push('/analytics/overview')"
              class="action-btn"
            >
              <el-icon><TrendCharts /></el-icon>
              <span>数据分析</span>
            </el-button>
          </div>
        </div>
      </el-col>

      <el-col :xs="24" :lg="8">
        <div class="content-card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Monitor /></el-icon>
              <span>系统状态</span>
            </div>
          </div>
          <div class="system-info">
            <div class="info-row">
              <span class="info-label">系统版本</span>
              <span class="info-value">v1.0.0</span>
            </div>
            <div class="info-row">
              <span class="info-label">最后更新</span>
              <span class="info-value">{{ formatTime(new Date()) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">用户角色</span>
              <el-tag :type="getRoleTagType(userRole)" size="small" effect="light">
                {{ getRoleLabel(userRole) }}
              </el-tag>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
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
  Document,
  Sunny,
  Lightning,
  Monitor,
  DataLine,
  Bell,
  DocumentRemove,
  PieChart,
  DataAnalysis,
  Edit,
  Star,
  Checked,
  Refresh
} from '@element-plus/icons-vue'
import BaseChart from '@/components/charts/BaseChart.vue'
import request from '@/api/request'

const authStore = useAuthStore()

const loading = ref(false)
const showWelcome = ref(true)
const errorMessage = ref('')

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

// 学习进度
const progressData = reactive({
  weeklyPercent: 0,
  weeklyCompleted: 0,
  pending: 0,
  streak: 0,
  beginner: 0,
  intermediate: 0,
  advanced: 0
})

const progressColors = [
  { color: '#EF4444', percentage: 20 },
  { color: '#F59E0B', percentage: 40 },
  { color: '#10B981', percentage: 60 },
  { color: '#3B82F6', percentage: 80 },
  { color: '#8B5CF6', percentage: 100 }
]

// 图表：分类
const categoryChartData = ref({ items: [], total: 0 })
const categoryChartOption = computed(() => {
  const items = categoryChartData.value.items
  if (!items.length) {
    return {
      title: { text: '暂无数据', left: 'center', top: 'middle', textStyle: { color: '#9CA3AF', fontSize: 14 } }
    }
  }
  return {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)',
      backgroundColor: 'rgba(17, 24, 39, 0.95)',
      borderColor: 'transparent',
      textStyle: { color: '#fff' }
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: { color: '#6B7280', fontSize: 12 },
      itemWidth: 10,
      itemHeight: 10,
      itemGap: 12
    },
    color: ['#2563EB', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#EC4899'],
    series: [
      {
        name: '分类',
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['38%', '50%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{d}%',
          fontSize: 11,
          color: '#374151'
        },
        labelLine: { show: true, length: 8, length2: 6 },
        data: items.map(i => ({ value: i.count, name: getCategoryLabel(i.category) }))
      }
    ]
  }
})

function getCategoryLabel(cat) {
  const map = {
    'zero_shot': '零样本',
    'few_shot': '少样本',
    'chain_of_thought': '思维链',
    'system_prompt': '系统提示',
    'role_playing': '角色扮演',
    'step_back': '后退提示',
    'prompt_chain': '提示链',
    'general': '通用',
  }
  return map[cat] || cat
}

function handleCategoryClick(params) {
  if (params.name) {
    // 跳转到学习列表并按分类筛选
    window.location.href = `/learning/list?category=${params.data?.name}`
  }
}

// 图表：分数趋势
const trendTabs = [
  { label: '近 7 天', value: 7 },
  { label: '近 30 天', value: 30 }
]
const trendRange = ref(7)
const scoreTrendRaw = ref([])

const scoreTrendOption = computed(() => {
  const range = trendRange.value
  const today = new Date()
  const dateMap = new Map()
  for (let i = range - 1; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const key = d.toISOString().slice(0, 10)
    dateMap.set(key, { score: null, count: 0, sum: 0 })
  }

  scoreTrendRaw.value.forEach(item => {
    const day = (item.created_at || '').slice(0, 10)
    if (dateMap.has(day)) {
      const entry = dateMap.get(day)
      entry.count += 1
      if (typeof item.overall_score === 'number') {
        entry.sum += item.overall_score
        entry.score = entry.sum / entry.count
      }
    }
  })

  const dates = []
  const scores = []
  const counts = []
  dateMap.forEach((val, key) => {
    dates.push(key.slice(5))
    scores.push(val.score !== null ? Math.round(val.score * 10) / 10 : null)
    counts.push(val.count)
  })

  if (scores.every(s => s === null)) {
    return {
      title: { text: '近 ' + range + ' 天暂无练习记录', left: 'center', top: 'middle', textStyle: { color: '#9CA3AF', fontSize: 14 } }
    }
  }

  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(17, 24, 39, 0.95)',
      borderColor: 'transparent',
      textStyle: { color: '#fff' },
      formatter: (params) => {
        const p = params[0]
        const idx = p.dataIndex
        return `${dates[idx]}<br/>平均分：<b>${scores[idx] ?? '无'}</b><br/>练习数：<b>${counts[idx]}</b>`
      }
    },
    grid: { left: 40, right: 30, top: 30, bottom: 30 },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: '#E5E7EB' } },
      axisLabel: { color: '#9CA3AF', fontSize: 11 },
      axisTick: { show: false }
    },
    yAxis: [
      {
        type: 'value',
        min: 0,
        max: 100,
        name: '分数',
        nameTextStyle: { color: '#9CA3AF', fontSize: 11 },
        splitLine: { lineStyle: { color: '#F3F4F6' } },
        axisLabel: { color: '#9CA3AF', fontSize: 11 }
      },
      {
        type: 'value',
        name: '次数',
        nameTextStyle: { color: '#9CA3AF', fontSize: 11 },
        splitLine: { show: false },
        axisLabel: { color: '#9CA3AF', fontSize: 11 }
      }
    ],
    series: [
      {
        name: '平均分',
        type: 'line',
        smooth: true,
        data: scores,
        yAxisIndex: 0,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { color: '#2563EB', width: 3 },
        itemStyle: { color: '#2563EB', borderColor: '#fff', borderWidth: 2 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(37, 99, 235, 0.25)' },
              { offset: 1, color: 'rgba(37, 99, 235, 0.02)' }
            ]
          }
        }
      },
      {
        name: '练习次数',
        type: 'bar',
        data: counts,
        yAxisIndex: 1,
        barWidth: 14,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#34D399' },
              { offset: 1, color: 'rgba(52, 211, 153, 0.3)' }
            ]
          },
          borderRadius: [4, 4, 0, 0]
        }
      }
    ]
  }
})

// 角色信息
const userRole = computed(() => authStore.role)
const isAdmin = computed(() => authStore.isAdmin)
const isAdminOrTeacher = computed(() => authStore.isAdminOrTeacher)
const username = computed(() => authStore.user?.username || '用户')

// 欢迎语
const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 11) return '早上好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const roleBasedTip = computed(() => {
  const tips = {
    admin: '建议优先查看用户活跃度与内容运营情况',
    teacher: '开始今天的内容创作或练习审核',
    student: '开启今日学习之旅，每天进步一点点'
  }
  return tips[userRole.value] || '祝您使用愉快'
})

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
    const [learningStatsRes, userStatsRes, practiceStatsRes, progressRes, recordsRes] = await Promise.allSettled([
      request({ url: '/learning/materials/statistics/', method: 'get', showError: false }),
      request({ url: '/users/statistics/', method: 'get', showError: false }),
      request({ url: '/practice/records/statistics/', method: 'get', showError: false }),
      request({ url: '/analytics/learning_progress/?period=7d', method: 'get', showError: false }),
      request({ url: '/practice/records/', method: 'get', params: { page_size: 200, ordering: '-created_at' }, showError: false })
    ])

    // 1. 顶部统计
    if (learningStatsRes.status === 'fulfilled' && learningStatsRes.value?.data) {
      const data = learningStatsRes.value.data
      stats.totalLearning = data.overview?.total || 0
      stats.publishedCount = data.overview?.published || 0
      // 分类饼图
      categoryChartData.value = {
        items: data.by_category || [],
        total: data.overview?.total || 0
      }
      // 最近活动
      if (data.recent_materials) {
        recentActivities.value = (data.recent_materials || []).slice(0, 6).map(item => ({
          id: item.id,
          user: item.author_name || '管理员',
          action: `发布了《${item.title}》`,
          actionType: 'publish',
          iconComponent: Edit,
          time: item.created_at
        }))
      }
    }

    if (userStatsRes.status === 'fulfilled' && userStatsRes.value?.data) {
      stats.totalUsers = userStatsRes.value.data.total || 0
    }

    if (practiceStatsRes.status === 'fulfilled' && practiceStatsRes.value?.data) {
      const data = practiceStatsRes.value.data
      stats.totalPractice = data.overview?.total || 0
      stats.avgScore = Math.round(data.overview?.avg_score || 0)
      stats.scoreLevel = stats.avgScore > 0 ? Math.ceil(stats.avgScore / 20) : 1
      stats.todayPractice = data.overview?.completed || 0
    }

    // 2. 学习进度
    if (progressRes.status === 'fulfilled' && progressRes.value?.data) {
      const data = progressRes.value.data
      const timeline = data.timeline || {}
      const completion = data.completion || {}
      const total = (timeline.completed_count || []).reduce((s, v) => s + (v || 0), 0)
      progressData.weeklyCompleted = total
      progressData.pending = stats.totalLearning - total > 0 ? stats.totalLearning - total : 0
      progressData.weeklyPercent = stats.totalLearning > 0
        ? Math.min(100, Math.round((total / stats.totalLearning) * 100))
        : 0
      progressData.streak = completion.streak_days || Math.min(total + 1, 7)

      // 按分类拆分成三档：入门/进阶/高级
      const cats = (categoryChartData.value.items || []).map(i => i.category)
      const beginner = ['zero_shot', 'general', 'system_prompt']
      const advanced = ['chain_of_thought', 'step_back', 'prompt_chain']
      const beginnerCount = cats.filter(c => beginner.includes(c)).length
      const advancedCount = cats.filter(c => advanced.includes(c)).length
      const intermediateCount = Math.max(0, cats.length - beginnerCount - advancedCount)
      const total3 = beginnerCount + intermediateCount + advancedCount || 1
      progressData.beginner = Math.round((beginnerCount / total3) * 100)
      progressData.intermediate = Math.round((intermediateCount / total3) * 100)
      progressData.advanced = Math.round((advancedCount / total3) * 100)
    } else {
      // 无数据时的回退
      progressData.weeklyPercent = 0
      progressData.weeklyCompleted = 0
      progressData.pending = stats.totalLearning
      progressData.streak = 0
    }

    // 3. 趋势原始数据
    if (recordsRes.status === 'fulfilled' && recordsRes.value?.data) {
      const list = recordsRes.value.data.results || recordsRes.value.data || []
      scoreTrendRaw.value = list
    }

    // 4. 兜底：若最近活动为空，则用练习记录补充
    if (recentActivities.value.length === 0 && recordsRes.status === 'fulfilled' && recordsRes.value?.data) {
      const list = recordsRes.value.data.results || recordsRes.value.data || []
      recentActivities.value = list.slice(0, 6).map(item => {
        const score = item.overall_score
        let actionType = 'complete'
        let iconComponent = Checked
        let action = `完成练习，得了 ${score} 分`
        if (score >= 90) {
          iconComponent = Star
          action = `练习得高分 ${score}，表现出色！`
        } else if (score < 60) {
          iconComponent = Refresh
          action = `完成练习，得了 ${score} 分`
        }
        return {
          id: item.id,
          user: item.user_info?.username || item.user?.username || '同学',
          action,
          actionType,
          iconComponent,
          time: item.created_at
        }
      })
    }

  } catch (error) {
    console.error('加载 Dashboard 数据失败:', error)
    if (error?.response?.status === 401) {
      errorMessage.value = '登录已过期，请重新登录'
    } else if (error?.response?.status === 403) {
      errorMessage.value = '没有权限访问此页面'
    } else {
      errorMessage.value = error?.message || '加载数据失败，请刷新页面重试'
    }
    setTimeout(() => { errorMessage.value = '' }, 5000)
  } finally {
    loading.value = false
    setTimeout(() => { showWelcome.value = false }, 5000)
  }
}

function getRoleTagType(role) {
  const map = { admin: 'danger', teacher: 'warning', student: '' }
  return map[role] || 'info'
}

function getRoleLabel(role) {
  const map = { admin: '管理员', teacher: '教师', student: '学生' }
  return map[role] || role
}

function formatTime(time) {
  if (!time) return '-'
  const date = new Date(time)
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.dashboard {
  min-height: 100%;
}

/* 欢迎横幅 */
.welcome-banner {
  background: linear-gradient(135deg, #2563EB 0%, #1E40AF 50%, #1E3A8A 100%);
  border-radius: 16px;
  padding: 32px 40px;
  color: #ffffff;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(37, 99, 235, 0.2);
}

.welcome-banner::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
  border-radius: 50%;
}

.welcome-banner::after {
  content: '';
  position: absolute;
  bottom: -30%;
  left: -5%;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(251, 191, 36, 0.1) 0%, transparent 70%);
  border-radius: 50%;
}

.welcome-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
  z-index: 1;
}

.welcome-left {
  flex: 1;
}

.welcome-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  line-height: 1.3;
}

.welcome-subtitle {
  font-size: 14px;
  margin: 0 0 12px 0;
  opacity: 0.85;
  font-weight: 400;
}

.welcome-tip {
  font-size: 14px;
  margin: 0;
  opacity: 0.9;
  background: rgba(255, 255, 255, 0.1);
  padding: 8px 16px;
  border-radius: 8px;
  display: inline-block;
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.welcome-illustration {
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-icon {
  color: #FBBF24;
  filter: drop-shadow(0 4px 12px rgba(251, 191, 36, 0.4));
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

/* 统计卡片 */
.stat-cards {
  margin-top: 0 !important;
}

.stat-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid #F3F4F6;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  height: 100%;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--card-color);
  opacity: 0;
  transition: opacity 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.08);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-card--blue { --card-color: #2563EB; }
.stat-card--blue .stat-icon { background: linear-gradient(135deg, #3B82F6, #1E40AF); }

.stat-card--green { --card-color: #10B981; }
.stat-card--green .stat-icon { background: linear-gradient(135deg, #34D399, #059669); }

.stat-card--orange { --card-color: #F59E0B; }
.stat-card--orange .stat-icon { background: linear-gradient(135deg, #FBBF24, #D97706); }

.stat-card--red { --card-color: #EF4444; }
.stat-card--red .stat-icon { background: linear-gradient(135deg, #F87171, #DC2626); }

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  flex-shrink: 0;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 30px;
  font-weight: 700;
  color: #111827;
  line-height: 1.2;
  margin-bottom: 4px;
  background: linear-gradient(135deg, #111827 0%, #374151 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 14px;
  color: #6B7280;
  margin-bottom: 8px;
  font-weight: 500;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.trend-up {
  color: #10B981;
  font-weight: 600;
  background-color: #ECFDF5;
  padding: 2px 8px;
  border-radius: 4px;
}

.trend-text {
  color: #9CA3AF;
}

/* 内容卡片（统一容器） */
.content-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #F3F4F6;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #F3F4F6;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
  color: #111827;
}

.card-title .el-icon {
  color: #2563EB;
  font-size: 18px;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  background: linear-gradient(135deg, #2563EB, #1E40AF);
  color: #ffffff;
  font-weight: 600;
}

.user-name {
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.action-tag {
  margin-right: 8px;
  font-weight: 500;
  border: none;
}

.action-desc {
  color: #4B5563;
  font-size: 14px;
}

.time-cell {
  color: #9CA3AF;
  font-size: 13px;
}

.activity-table {
  border-radius: 8px;
}

/* === 学习进度卡片 === */
.progress-card .progress-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-top: 4px;
}

.progress-main {
  display: flex;
  align-items: center;
  gap: 28px;
  padding: 16px 0 4px;
}

.progress-ring {
  flex-shrink: 0;
}

.progress-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.progress-info .info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #F9FAFB;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.progress-info .info-item:hover {
  background: #F3F4F6;
}

.progress-info .info-label {
  color: #6B7280;
  font-size: 13px;
}

.progress-info .info-value {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
}

.progress-info .info-value.pending {
  color: #F59E0B;
}

.progress-info .info-value.streak {
  color: #EF4444;
}

.progress-bar-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 4px 0 0;
  border-top: 1px solid #F3F4F6;
  padding-top: 16px;
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bar-label {
  width: 40px;
  font-size: 13px;
  color: #6B7280;
  font-weight: 500;
  flex-shrink: 0;
}

.bar-track {
  flex: 1;
  height: 8px;
  background: #F3F4F6;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.bar-value {
  width: 40px;
  text-align: right;
  font-size: 13px;
  font-weight: 600;
  color: #111827;
  flex-shrink: 0;
}

/* === 活动列表 === */
.activity-list {
  min-height: 200px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #F3F4F6;
  transition: background-color 0.2s;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-item:hover {
  background-color: #FAFAFA;
  margin: 0 -12px;
  padding: 12px;
  border-radius: 8px;
  border-bottom-color: transparent;
}

.activity-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #ffffff;
}

.activity-icon--publish { background: linear-gradient(135deg, #3B82F6, #1E40AF); }
.activity-icon--create { background: linear-gradient(135deg, #F59E0B, #D97706); }
.activity-icon--complete { background: linear-gradient(135deg, #10B981, #059669); }
.activity-icon--update { background: linear-gradient(135deg, #6B7280, #4B5563); }
.activity-icon--system { background: linear-gradient(135deg, #8B5CF6, #6D28D9); }

.activity-body {
  flex: 1;
  min-width: 0;
}

.activity-desc {
  font-size: 14px;
  color: #111827;
  line-height: 1.5;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.activity-user {
  font-weight: 600;
  color: #1E40AF;
}

.activity-text {
  color: #4B5563;
}

.activity-time {
  font-size: 12px;
  color: #9CA3AF;
  margin-top: 4px;
}

.activity-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #9CA3AF;
}

.activity-empty p {
  margin: 12px 0 0;
  font-size: 14px;
}

.activity-fade-enter-active,
.activity-fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.activity-fade-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.activity-fade-leave-to {
  opacity: 0;
  transform: translateX(8px);
}

/* === 图表 Tabs === */
.chart-tabs {
  display: flex;
  gap: 4px;
  background: #F3F4F6;
  padding: 3px;
  border-radius: 8px;
}

.chart-tabs .tab-item {
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 6px;
  cursor: pointer;
  color: #6B7280;
  transition: all 0.2s;
  user-select: none;
}

.chart-tabs .tab-item:hover {
  color: #111827;
}

.chart-tabs .tab-item.active {
  background: #ffffff;
  color: #2563EB;
  font-weight: 600;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* 快捷操作 */
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
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: none;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.action-btn .el-icon {
  font-size: 16px;
}

/* 系统状态 */
.system-info {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: #F9FAFB;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.info-row:hover {
  background: #F3F4F6;
}

.info-label {
  color: #6B7280;
  font-size: 13px;
  font-weight: 500;
}

.info-value {
  color: #111827;
  font-size: 13px;
  font-weight: 600;
}

/* 响应式 */
@media (max-width: 768px) {
  .welcome-banner {
    padding: 24px;
  }

  .welcome-title {
    font-size: 22px;
  }

  .welcome-illustration {
    display: none;
  }

  .stat-card {
    padding: 18px;
  }

  .stat-value {
    font-size: 24px;
  }
}
</style>
