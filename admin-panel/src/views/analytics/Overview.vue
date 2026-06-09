<template>
  <div class="analytics-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>{{ isTeacher ? '📊 我的班级数据分析' : '📊 数据分析中心' }}</h2>
      <div class="header-actions">
        <el-select
          v-if="isTeacher && myClasses.length > 0"
          v-model="selectedClassId"
          placeholder="全部班级"
          clearable
          style="width: 180px; margin-right: 10px;"
        >
          <el-option
            v-for="cls in myClasses"
            :key="cls.id"
            :label="`${cls.name} (${cls.student_count}人)`"
            :value="cls.id"
          />
        </el-select>
        <el-select v-model="period" placeholder="选择时间范围" style="width: 150px">
        <el-option label="最近7天" value="7d" />
        <el-option label="最近30天" value="30d" />
        <el-option label="最近90天" value="90d" />
      </el-select>
      </div>
    </div>

    <el-empty
      v-if="isTeacher && myClasses.length === 0 && !loading"
      description="您暂未管理任何班级和学生"
      :image-size="120"
    >
      <el-button type="primary">联系管理员分配班级</el-button>
    </el-empty>

    <el-row :gutter="20" v-loading="loading" v-else>
      <!-- 核心指标卡片 -->
      <el-col :span="6" v-for="(stat, index) in coreStats" :key="index">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" :style="{ background: stat.color }">
            {{ stat.icon }}
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
            <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
              {{ stat.trend > 0 ? '↑' : '↓' }} {{ Math.abs(stat.trend) }}%
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 趋势图 -->
      <el-col :span="16">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>📈 数据趋势</span>
          </template>
          <LineChart
            :x-axis-data="trendData.dates"
            :series-data="trendData.values"
            height="350px"
            title=""
            :show-area="true"
          />
        </el-card>
      </el-col>

      <!-- 热门内容排行 -->
      <el-col :span="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>🔥 热门内容 TOP10</span>
          </template>
          <el-table
            :data="topContent"
            size="small"
            style="width: 100%"
            max-height="400"
          >
            <el-table-column prop="title" label="标题" show-overflow-tooltip />
            <el-table-column prop="views" label="阅读量" width="80" align="center" />
            <el-table-column prop="completions" label="完成数" width="80" align="center" />
          </el-table>
        </el-card>
      </el-col>

      <!-- 优秀学员排行 (仅管理员/教师可见) -->
      <el-col :span="12" v-if="showUserRanking">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>🏆 {{ isTeacher ? '班级学员排行' : '优秀学员排行' }}</span>
          </template>
          <el-table
            :data="topUsers"
            size="small"
            style="width: 100%"
            max-height="400"
          >
            <el-table-column type="index" label="#" width="50" align="center" />
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="role" label="角色" width="80" align="center" />
            <el-table-column prop="total_practices" label="练习次数" width="90" align="center" />
            <el-table-column prop="avg_score" label="平均分" width="80" align="center">
              <template #default="{ row }">
                <el-tag :type="row.avg_score >= 80 ? 'success' : row.avg_score >= 60 ? 'warning' : 'danger'" size="small">
                  {{ row.avg_score }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 学习 vs 练习对比 -->
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>📊 学习与练习对比</span>
          </template>
          <BarChart
            :x-axis-data="['学习资料', '练习记录']"
            :series-data="[overviewData.learning?.total_materials || 0, overviewData.practice?.total_records || 0]"
            height="300px"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/store/modules/auth'
import LineChart from '@/components/charts/LineChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import { getAnalyticsOverview } from '@/api/analytics'
import { getMyClasses } from '@/api/auth'

const authStore = useAuthStore()
const loading = ref(false)
const period = ref('30d')
const overviewData = ref({})

const isTeacher = computed(() => ['admin', 'teacher'].includes(authStore.userInfo?.role || ''))
const userRole = computed(() => authStore.userInfo?.role || '')
const showUserRanking = computed(() => ['admin', 'teacher'].includes(userRole.value))

// 班级选择器
const myClasses = ref([])
const selectedClassId = ref(null)

const loadMyClasses = async () => {
  if (!isTeacher.value) return
  try {
    const res = await getMyClasses()
    if (res.code === 200) {
      myClasses.value = res.data || []
    }
  } catch (e) { /* 静默 */ }
}

const coreStats = computed(() => [
  {
    icon: '📚',
    label: '学习资料总数',
    value: overviewData.value.learning?.total_materials || 0,
    color: '#409EFF',
    trend: 5.2
  },
  {
    icon: '✏️',
    label: '练习总记录',
    value: overviewData.value.practice?.total_records || 0,
    color: '#67C23A',
    trend: 8.7
  },
  {
    icon: '👥',
    label: '今日活跃用户',
    value: overviewData.value.users?.active_today || 0,
    color: '#E6A23C',
    trend: -2.1
  },
  {
    icon: '🎯',
    label: '平均练习分数',
    value: overviewData.value.practice?.avg_score || 0,
    color: '#F56C6C',
    trend: 3.4
  }
])

const trendData = computed(() => {
  const dailyTrend = overviewData.value.daily_trend || []
  return {
    dates: dailyTrend.map(item => item.date),
    values: dailyTrend.map(item => item.count)
  }
})

const topContent = computed(() => overviewData.value.top_content || [])
const topUsers = computed(() => overviewData.value.top_users || [])

const fetchOverview = async () => {
  loading.value = true
  try {
    const params = { period: period.value }
    if (selectedClassId.value) {
      params.class_id = selectedClassId.value
    }
    const res = await getAnalyticsOverview(params)
    if (res.code === 200) {
      overviewData.value = res.data
    }
  } catch (error) {
    console.error('获取数据概览失败:', error)
  } finally {
    loading.value = false
  }
}

watch([period, selectedClassId], () => {
  fetchOverview()
})

onMounted(async () => {
  await loadMyClasses()
  fetchOverview()
})
</script>

<style scoped lang="scss">
.analytics-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  h2 {
    margin: 0;
    font-size: 24px;
    color: #303133;
  }

  .header-actions {
    display: flex;
    align-items: center;
  }
}

.stat-card {
  margin-bottom: 20px;
  
  :deep(.el-card__body) {
    display: flex;
    align-items: center;
    padding: 15px;
  }

  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    margin-right: 15px;
  }

  .stat-content {
    flex: 1;

    .stat-value {
      font-size: 28px;
      font-weight: bold;
      color: #303133;
      line-height: 1.2;
    }

    .stat-label {
      font-size: 14px;
      color: #909399;
      margin-top: 4px;
    }

    .stat-trend {
      font-size: 13px;
      margin-top: 4px;
      
      &.up {
        color: #67C23A;
      }

      &.down {
        color: #F56C6C;
      }
    }
  }
}

.chart-card {
  margin-bottom: 20px;

  .chart-title {
    font-size: 16px;
    font-weight: bold;
    color: #303133;
  }
}
</style>
