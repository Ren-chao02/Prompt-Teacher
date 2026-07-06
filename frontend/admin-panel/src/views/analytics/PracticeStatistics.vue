<template>
  <div class="practice-statistics-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>{{ isTeacher ? '✏️ 我的班级练习成绩' : '✏️ 练习成绩统计分析' }}</h2>
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
        <el-select v-model="period" placeholder="时间范围" style="width: 150px; margin-right: 10px;">
          <el-option label="最近7天" value="7d" />
          <el-option label="最近30天" value="30d" />
          <el-option label="最近90天" value="90d" />
        </el-select>
        <el-select v-model="scoreLevelFilter" placeholder="分数等级" clearable style="width: 140px; margin-right: 10px;">
          <el-option label="优秀 (90-100)" value="excellent" />
          <el-option label="良好 (80-89)" value="good" />
          <el-option label="中等 (70-79)" value="average" />
          <el-option label="不及格 (<60)" value="fail" />
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
            <el-tag 
              :type="stat.tagType" 
              size="small"
              style="margin-top: 8px;"
            >
              {{ stat.trend }}
            </el-tag>
          </div>
        </el-card>
      </el-col>

      <!-- 成绩趋势图 -->
      <el-col :span="16">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>📈 成绩变化趋势</span>
          </template>
          <LineChart
            :x-axis-data="statisticsData.score_trend?.dates || []"
            :series-data="statisticsData.score_trend?.scores || []"
            height="350px"
            title=""
            :show-area="true"
          />
          <div style="margin-top: 15px; padding: 10px; background: #f5f7fa; border-radius: 6px;">
            <el-descriptions :column="3" size="small" border>
              <el-descriptions-item label="平均分">
                <strong style="color: #409EFF; font-size: 16px;">
                  {{ statisticsData.score_trend?.avg_score || 0 }}
                </strong>
              </el-descriptions-item>
              <el-descriptions-item label="数据点数">
                <strong>{{ (statisticsData.score_trend?.dates || []).length }} 天</strong>
              </el-descriptions-item>
              <el-descriptions-item label="最高分">
                <strong style="color: #67C23A;">
                  {{ maxScore || 0 }}
                </strong>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>

      <!-- 分数分布 -->
      <el-col :span="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>📊 分数分布</span>
          </template>
          <PieChart
            :data="scoreDistributionData"
            height="280px"
            title=""
          />
          
          <!-- 统计摘要 -->
          <div style="margin-top: 15px; padding: 12px; background: #f5f7fa; border-radius: 6px;">
            <el-row :gutter="12">
              <el-col :span="8" style="text-align: center;">
                <div style="font-size: 18px; font-weight: bold; color: #303133;">
                  {{ statisticsData.distribution?.mean || 0 }}
                </div>
                <div style="font-size: 12px; color: #909399;">均值</div>
              </el-col>
              <el-col :span="8" style="text-align: center;">
                <div style="font-size: 18px; font-weight: bold; color: #303133;">
                  {{ statisticsData.distribution?.median || 0 }}
                </div>
                <div style="font-size: 12px; color: #909399;">中位数</div>
              </el-col>
              <el-col :span="8" style="text-align: center;">
                <div style="font-size: 18px; font-weight: bold; color: #303133;">
                  {{ statisticsData.distribution?.std_dev || 0 }}
                </div>
                <div style="font-size: 12px; color: #909399;">标准差</div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>

      <!-- 各场景表现对比 -->
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>🎯 各场景表现对比</span>
          </template>
          <BarChart
            :x-axis-data="scenarioComparisonLabels"
            :series-data="scenarioComparisonScores"
            height="300px"
            title=""
            :horizontal="true"
          />
        </el-card>
      </el-col>

      <!-- 薄弱点识别 -->
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>⚠️ 薄弱点识别</span>
          </template>
          <el-table
            :data="weakPoints"
            size="small"
            style="width: 100%"
            max-height="320"
            stripe
            :row-class-name="tableRowClassName"
          >
            <el-table-column prop="topic_title" label="知识点" show-overflow-tooltip />
            <el-table-column prop="error_rate" label="错误率" width="90" align="center">
              <template #default="{ row }">
                <el-progress
                  :percentage="row.error_rate"
                  :stroke-width="14"
                  :text-inside="true"
                  :color="getErrorColor(row.error_rate)"
                  status="exception"
                />
              </template>
            </el-table-column>
            <el-table-column prop="total_attempts" label="尝试次数" width="85" align="center" />
            <el-table-column prop="suggestion" label="建议" show-overflow-tooltip width="120">
              <template #default="{ row }">
                <el-tooltip :content="row.suggestion" placement="top">
                  <el-button type="primary" link size="small">查看建议</el-button>
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>
          
          <el-empty 
            v-if="weakPoints.length === 0" 
            description="暂无薄弱点数据，继续保持！"
            :image-size="80"
          />
        </el-card>
      </el-col>

      <!-- 练习排行榜 (仅管理员/教师可见) -->
      <el-col :span="24" v-if="showRanking">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>🏆 {{ isTeacher ? '班级练习排行榜' : '练习排行榜' }} TOP20</span>
              <el-radio-group v-model="rankingType" size="small">
                <el-radio-button label="score">按分数</el-radio-button>
                <el-radio-button label="count">按次数</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <el-table
            :data="sortedRanking"
            size="small"
            style="width: 100%"
            stripe
          >
            <el-table-column type="index" label="#" width="60" align="center">
              <template #default="{ $index }">
                <el-badge 
                  :value="$index + 1" 
                  :type="$index < 3 ? 'warning' : 'info'"
                  class="rank-badge"
                >
                  <span>{{ $index + 1 }}</span>
                </el-badge>
              </template>
            </el-table-column>
            <el-table-column label="用户" min-width="180">
              <template #default="{ row }">
                <div style="display: flex; align-items: center; gap: 10px;">
                  <el-avatar 
                    :size="32" 
                    :src="row.avatar || undefined"
                  >
                    {{ row.username?.charAt(0)?.toUpperCase() }}
                  </el-avatar>
                  <span>{{ row.username }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="total_practices" label="总练习次数" width="110" align="center">
              <template #default="{ row }">
                <el-tag type="primary" size="small">{{ row.total_practices }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="avg_score" label="平均分" width="100" align="center">
              <template #default="{ row }">
                <el-tag 
                  :type="getScoreTagType(row.avg_score)" 
                  size="small"
                  effect="dark"
                >
                  {{ row.avg_score }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="best_score" label="最高分" width="90" align="center">
              <template #default="{ row }">
                <strong style="color: #67C23A;">{{ row.best_score }}</strong>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 详细场景对比表格 -->
      <el-col :span="24">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>📋 场景详细对比表</span>
          </template>
          <el-table
            :data="scenarioComparison"
            size="small"
            style="width: 100%"
            border
          >
            <el-table-column prop="scenario_title" label="场景名称" min-width="200" />
            <el-table-column prop="icon" label="图标" width="70" align="center">
              <template #default="{ row }">
                <span style="font-size: 20px;">{{ row.icon || '📊' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="difficulty" label="难度" width="90" align="center">
              <template #default="{ row }">
                <el-tag 
                  :type="getDifficultyTagType(row.difficulty)" 
                  size="small"
                >
                  {{ getDifficultyLabel(row.difficulty) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="avg_score" label="平均分" width="95" align="center" sortable>
              <template #default="{ row }">
                <el-progress
                  :percentage="row.avg_score"
                  :stroke-width="14"
                  :text-inside="true"
                  :color="getScoreProgressColor(row.avg_score)"
                />
              </template>
            </el-table-column>
            <el-table-column prop="practice_count" label="练习次数" width="100" align="center" sortable />
            <el-table-column prop="best_score" label="最佳成绩" width="100" align="center" sortable>
              <template #default="{ row }">
                <strong :style="{ color: row.best_score >= 90 ? '#67C23A' : '#409EFF' }">
                  {{ row.best_score }}
                </strong>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/modules/auth'
import LineChart from '@/components/charts/LineChart.vue'
import BarChart from '@/components/charts/BarChart.vue'
import PieChart from '@/components/charts/PieChart.vue'
import { getPracticeStatistics } from '@/api/analytics'
import { getMyClasses } from '@/api/auth'

const authStore = useAuthStore()
const loading = ref(false)
const period = ref('30d')
const scoreLevelFilter = ref('')
const rankingType = ref('score')
const statisticsData = ref({})

const isTeacher = computed(() => ['admin', 'teacher'].includes(authStore.userInfo?.role || ''))
const userRole = computed(() => authStore.userInfo?.role || '')
const showRanking = computed(() => ['admin', 'teacher'].includes(userRole.value))

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
    icon: '📝',
    label: '总练习记录',
    value: totalRecords.value,
    color: '#409EFF',
    tagType: '',
    trend: ''
  },
  {
    icon: '⭐',
    label: '平均分数',
    value: avgScore.value,
    color: '#67C23A',
    tagType: getScoreTagType(avgScore.value),
    trend: getScoreLabel(avgScore.value)
  },
  {
    icon: '✅',
    label: '通过率',
    value: `${passRate.value}%`,
    color: '#E6A23C',
    tagType: passRate.value >= 80 ? 'success' : passRate.value >= 60 ? 'warning' : 'danger',
    trend: passRate.value >= 80 ? '优秀' : passRate.value >= 60 ? '良好' : '需努力'
  },
  {
    icon: '🎯',
    label: '最高分',
    value: maxScore.value,
    color: '#F56C6C',
    tagType: 'success',
    trend: '最佳成绩'
  }
])

const totalRecords = computed(() => {
  const scores = statisticsData.value.score_trend?.scores || []
  return scores.length
})

const avgScore = computed(() => statisticsData.value.score_trend?.avg_score || 0)

const maxScore = computed(() => {
  const scores = statisticsData.value.score_trend?.scores || []
  return Math.max(...scores, 0)
})

const passRate = computed(() => {
  const dist = statisticsData.value.distribution || {}
  const total = (dist.excellent || 0) + (dist.good || 0) + (dist.average || 0) + 
               (dist.below_average || 0) + (dist.fail || 0)
  if (total === 0) return 0
  
  const passed = (dist.excellent || 0) + (dist.good || 0) + (dist.average || 0) + 
                 (dist.below_average || 0)
  return Math.round((passed / total) * 100)
})

const scoreDistributionData = computed(() => {
  const dist = statisticsData.value.distribution || {}
  return [
    { name: '优秀 (90-100)', value: dist.excellent || 0 },
    { name: '良好 (80-89)', value: dist.good || 0 },
    { name: '中等 (70-79)', value: dist.average || 0 },
    { name: '及格 (60-69)', value: dist.below_average || 0 },
    { name: '不及格 (<60)', value: dist.fail || 0 }
  ].filter(item => item.value > 0)
})

const scenarioComparison = computed(() => statisticsData.value.scenario_comparison || [])
const scenarioComparisonLabels = computed(() => scenarioComparison.value.map(s => s.scenario_title))
const scenarioComparisonScores = computed(() => scenarioComparison.value.map(s => s.avg_score))
const weakPoints = computed(() => statisticsData.value.weak_points || [])

const ranking = computed(() => statisticsData.value.ranking || [])
const sortedRanking = computed(() => {
  if (!ranking.value || ranking.value.length === 0) return []
  
  const sorted = [...ranking.value]
  if (rankingType.value === 'score') {
    sorted.sort((a, b) => b.avg_score - a.avg_score)
  } else {
    sorted.sort((a, b) => b.total_practices - a.total_practices)
  }
  
  return sorted.slice(0, 20)
})

function getScoreTagType(score) {
  if (score >= 90) return 'success'
  if (score >= 80) return ''
  if (score >= 60) return 'warning'
  return 'danger'
}

function getScoreLabel(score) {
  if (score >= 90) return '优秀'
  if (score >= 80) return '良好'
  if (score >= 60) return '中等'
  return '需努力'
}

function getErrorColor(rate) {
  if (rate >= 70) return '#F56C6C'
  if (rate >= 50) return '#E6A23C'
  return '#409EFF'
}

function tableRowClassName({ row }) {
  if (row.error_rate >= 70) return 'warning-row'
  return ''
}

function getDifficultyTagType(difficulty) {
  const types = {
    'beginner': 'info',
    'intermediate': '',
    'advanced': 'warning',
    'expert': 'danger'
  }
  return types[difficulty] || 'info'
}

function getDifficultyLabel(difficulty) {
  const labels = {
    'beginner': '初级',
    'intermediate': '中级',
    'advanced': '高级',
    'expert': '专家'
  }
  return labels[difficulty] || difficulty
}

function getScoreProgressColor(score) {
  if (score >= 90) return '#67C23A'
  if (score >= 80) return '#409EFF'
  if (score >= 70) return '#E6A23C'
  return '#F56C6C'
}

const fetchStatistics = async () => {
  loading.value = true
  try {
    const params = { period: period.value }
    if (scoreLevelFilter.value) {
      params.score_level = scoreLevelFilter.value
    }
    if (selectedClassId.value) {
      params.class_id = selectedClassId.value
    }

    const res = await getPracticeStatistics(params)
    if (res.code === 200) {
      statisticsData.value = res.data
    }
  } catch (error) {
    console.error('获取练习统计失败:', error)
  } finally {
    loading.value = false
  }
}

watch([period, scoreLevelFilter, selectedClassId], () => {
  fetchStatistics()
})

onMounted(async () => {
  await loadMyClasses()
  fetchStatistics()
})
</script>

<style scoped lang="scss">
.practice-statistics-container {
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
  }
}

.chart-card {
  margin-bottom: 20px;
}

.rank-badge {
  :deep(.el-badge__content) {
    font-size: 13px !important;
  }
}

:deep(.warning-row) {
  background-color: #fdf6ec !important;
}
</style>
