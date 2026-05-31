<template>
  <div class="learning-progress-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>📚 学习进度分析</h2>
      <div class="header-actions">
        <el-select v-model="period" placeholder="时间范围" style="width: 150px; margin-right: 10px;">
          <el-option label="最近7天" value="7d" />
          <el-option label="最近30天" value="30d" />
          <el-option label="最近90天" value="90d" />
          <el-option label="全部" value="all" />
        </el-select>
        <el-select v-model="categoryFilter" placeholder="分类筛选" clearable style="width: 180px;">
          <el-option label="基础入门" value="basic" />
          <el-option label="进阶技巧" value="intermediate" />
          <el-option label="高级应用" value="advanced" />
          <el-option label="最佳实践" value="best_practices" />
        </el-select>
      </div>
    </div>

    <el-row :gutter="20" v-loading="loading">
      <!-- 学习时间线 -->
      <el-col :span="16">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>📈 学习时间线</span>
          </template>
          <LineChart
            :x-axis-data="progressData.timeline?.dates || []"
            :series-data="progressData.timeline?.read_minutes || []"
            height="350px"
            title=""
            :show-area="true"
          />
          <div style="margin-top: 15px; display: flex; justify-content: space-around; text-align: center;">
            <div>
              <div style="font-size: 24px; font-weight: bold; color: #409EFF;">
                {{ totalReadMinutes }} 分钟
              </div>
              <div style="color: #909399; font-size: 13px;">总阅读时长</div>
            </div>
            <div>
              <div style="font-size: 24px; font-weight: bold; color: #67C23A;">
                {{ completedCount }}
              </div>
              <div style="color: #909399; font-size: 13px;">完成数量</div>
            </div>
            <div>
              <div style="font-size: 24px; font-weight: bold; color: #E6A23C;">
                {{ avgDailyMinutes }} 分钟
              </div>
              <div style="color: #909399; font-size: 13px;">日均学习</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 完成情况分布 -->
      <el-col :span="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>📊 分类完成情况</span>
          </template>
          <PieChart
            :data="categoryCompletionData"
            height="300px"
            title=""
          />
        </el-card>
        
        <!-- 整体完成率 -->
        <el-card shadow="hover" style="margin-top: 20px;">
          <div style="text-align: center; padding: 20px;">
            <el-progress
              type="circle"
              :percentage="overallRate"
              :width="140"
              :stroke-width="12"
              color="#67C23A"
            >
              <template #default="{ percentage }">
                <span style="font-size: 24px; font-weight: bold;">{{ percentage }}%</span>
                <br>
                <span style="font-size: 13px; color: #909399;">整体完成率</span>
              </template>
            </el-progress>
          </div>
        </el-card>
      </el-col>

      <!-- 热门内容排行 -->
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>🔥 热门内容 TOP10</span>
          </template>
          <el-table
            :data="popularContent"
            size="small"
            style="width: 100%"
            max-height="400"
            stripe
          >
            <el-table-column type="index" label="#" width="50" align="center" />
            <el-table-column prop="title" label="标题" show-overflow-tooltip />
            <el-table-column prop="views" label="阅读量" width="80" align="center">
              <template #default="{ row }">
                <el-tag type="primary" size="small">{{ row.views }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="completions" label="完成数" width="80" align="center">
              <template #default="{ row }">
                <el-tag type="success" size="small">{{ row.completions }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 学习习惯分析 -->
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>🕐 学习习惯分析</span>
          </template>
          
          <div style="padding: 10px;">
            <!-- 高峰时段 -->
            <div style="margin-bottom: 25px;">
              <h4 style="margin: 0 0 10px 0; color: #303133; font-size: 14px;">⏰ 高峰学习时段</h4>
              <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <el-tag 
                  v-for="(hour, index) in peakHours" 
                  :key="index"
                  type="warning"
                  effect="dark"
                  size="large"
                >
                  {{ hour }}:00 - {{ hour + 1 }}:00
                </el-tag>
                <el-tag v-if="peakHours.length === 0" type="info">暂无数据</el-tag>
              </div>
            </div>

            <!-- 平均时长 -->
            <div style="margin-bottom: 25px;">
              <h4 style="margin: 0 0 10px 0; color: #303133; font-size: 14px;">⏱️ 平均单次学习时长</h4>
              <el-statistic :value="avgSessionDuration" suffix="分钟" />
            </div>

            <!-- 偏好分类 -->
            <div style="margin-bottom: 25px;">
              <h4 style="margin: 0 0 10px 0; color: #303133; font-size: 14px;">📂 偏好内容类型</h4>
              <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                <el-tag 
                  v-for="(cat, index) in preferredCategories" 
                  :key="index"
                  :type="['primary', 'success', 'warning', 'danger'][index % 4]"
                  size="large"
                >
                  {{ getCategoryLabel(cat) }}
                </el-tag>
                <el-tag v-if="preferredCategories.length === 0" type="info">暂无数据</el-tag>
              </div>
            </div>

            <!-- 活跃天数 -->
            <div>
              <h4 style="margin: 0 0 10px 0; color: #303133; font-size: 14px;">📅 近期活跃度</h4>
              <el-progress
                :percentage="activeDaysPercentage"
                :stroke-width="18"
                :text-inside="true"
                status="success"
              >
                <span>{{ activeDaysSample }}/7 天</span>
              </el-progress>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import LineChart from '@/components/charts/LineChart.vue'
import PieChart from '@/components/charts/PieChart.vue'
import { getLearningProgress } from '@/api/analytics'

const loading = ref(false)
const period = ref('30d')
const categoryFilter = ref('')
const progressData = ref({})

const totalReadMinutes = computed(() => {
  const minutes = progressData.value.timeline?.read_minutes || []
  return minutes.reduce((sum, val) => sum + (val || 0), 0)
})

const completedCount = computed(() => {
  const counts = progressData.value.timeline?.completed_count || []
  return counts.reduce((sum, val) => sum + (val || 0), 0)
})

const avgDailyMinutes = computed(() => {
  const dates = progressData.value.timeline?.dates || []
  if (dates.length === 0) return 0
  return Math.round(totalReadMinutes.value / dates.length)
})

const overallRate = computed(() => {
  return Math.round(progressData.value.completion?.overall_rate || 0)
})

const categoryCompletionData = computed(() => {
  const byCategory = progressData.value.completion?.by_category || {}
  return Object.entries(byCategory).map(([category, stats]) => ({
    name: getCategoryLabel(category),
    value: stats.completed || 0,
    count: stats.total || 0
  }))
})

const popularContent = computed(() => progressData.value.popular_content || [])

const peakHours = computed(() => progressData.value.reading_habits?.peak_hours || [])
const avgSessionDuration = computed(() => progressData.value.reading_habits?.avg_session_duration || 0)
const preferredCategories = computed(() => progressData.value.reading_habits?.preferred_categories || [])
const activeDaysSample = computed(() => progressData.value.reading_habits?.active_days_sample || 0)
const activeDaysPercentage = computed(() => Math.round((activeDaysSample.value / 7) * 100))

function getCategoryLabel(category) {
  const labels = {
    'basic': '基础入门',
    'intermediate': '进阶技巧',
    'advanced': '高级应用',
    'best_practices': '最佳实践',
    '未分类': '未分类'
  }
  return labels[category] || category
}

const fetchProgress = async () => {
  loading.value = true
  try {
    const params = { period: period.value }
    if (categoryFilter.value) {
      params.category = categoryFilter.value
    }
    
    const res = await getLearningProgress(params)
    if (res.code === 200) {
      progressData.value = res.data
    }
  } catch (error) {
    console.error('获取学习进度失败:', error)
  } finally {
    loading.value = false
  }
}

watch([period, categoryFilter], () => {
  fetchProgress()
})

onMounted(() => {
  fetchProgress()
})
</script>

<style scoped lang="scss">
.learning-progress-container {
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

.chart-card {
  margin-bottom: 20px;

  .chart-title {
    font-size: 16px;
    font-weight: bold;
    color: #303133;
  }
}
</style>
