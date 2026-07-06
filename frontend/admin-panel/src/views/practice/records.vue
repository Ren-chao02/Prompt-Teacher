<template>
  <div class="records-management">
    <div class="page-header">
      <h2>练习记录</h2>
      <div class="header-actions">
        <el-button type="success" @click="handleExport">
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ statistics.total || 0 }}</div>
            <div class="stat-label">总记录数</div>
          </div>
          <el-icon class="stat-icon"><Document /></el-icon>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card success">
          <div class="stat-content">
            <div class="stat-value">{{ statistics.completed || 0 }}</div>
            <div class="stat-label">已完成</div>
          </div>
          <el-icon class="stat-icon"><CircleCheck /></el-icon>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card warning">
          <div class="stat-content">
            <div class="stat-value">{{ statistics.avg_score?.toFixed(1) || '0.0' }}</div>
            <div class="stat-label">平均分</div>
          </div>
          <el-icon class="stat-icon"><TrendCharts /></el-icon>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card danger">
          <div class="stat-content">
            <div class="stat-value">{{ formatDuration(statistics.total_duration) }}</div>
            <div class="stat-label">总用时</div>
          </div>
          <el-icon class="stat-icon"><Timer /></el-icon>
        </el-card>
      </el-col>
    </el-row>

    <!-- 高级筛选面板 -->
    <el-card class="filter-card" shadow="never">
      <template #header>
        <div class="filter-header">
          <span>高级筛选</span>
          <el-button text size="small" @click="toggleFilters">
            {{ showAdvancedFilters ? '收起' : '展开' }}
            <el-icon><ArrowDown v-if="!showAdvancedFilters" /><ArrowUp v-else /></el-icon>
          </el-button>
        </div>
      </template>

      <el-collapse-transition>
        <div v-show="showAdvancedFilters">
          <el-form :model="filters" label-width="100px" inline>
            <el-form-item label="关键词">
              <el-input
                v-model="filters.keyword"
                placeholder="搜索提示词/建议"
                clearable
                style="width: 200px;"
                @keyup.enter="loadData"
              />
            </el-form-item>

            <el-form-item label="用户">
              <el-input
                v-model="filters.user"
                placeholder="用户名"
                clearable
                style="width: 150px;"
              />
            </el-form-item>

            <el-form-item label="场景">
              <el-select
                v-model="filters.scenario"
                placeholder="选择场景"
                clearable
                filterable
                style="width: 200px;"
              >
                <el-option
                  v-for="s in scenarios"
                  :key="s.id"
                  :label="s.title"
                  :value="s.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="成绩等级">
              <el-select v-model="filters.score_level" placeholder="等级" clearable style="width: 140px;">
                <el-option label="优秀 (90-100)" value="excellent" />
                <el-option label="良好 (80-89)" value="good" />
                <el-option label="中等 (70-79)" value="average" />
                <el-option label="待提高 (60-69)" value="needs_improvement" />
                <el-option label="较差 (<60)" value="poor" />
              </el-select>
            </el-form-item>

            <el-form-item label="完成状态">
              <el-select v-model="filters.is_completed" placeholder="状态" clearable style="width: 120px;">
                <el-option label="已完成" :value="true" />
                <el-option label="未完成" :value="false" />
              </el-select>
            </el-form-item>

            <el-form-item label="分数范围">
              <el-input-number
                v-model="filters.score_min"
                :min="0"
                :max="100"
                placeholder="最低"
                style="width: 110px;"
              />
              <span style="margin: 0 8px;">-</span>
              <el-input-number
                v-model="filters.score_max"
                :min="0"
                :max="100"
                placeholder="最高"
                style="width: 110px;"
              />
            </el-form-item>

            <el-form-item label="时间范围">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 260px;"
              />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" icon="Search" @click="loadData">搜索</el-button>
              <el-button icon="Refresh" @click="resetFilters">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-collapse-transition>
    </el-card>

    <!-- 数据表格 -->
    <el-table
      :data="records"
      stripe
      border
      v-loading="loading"
      @row-click="handleViewDetail"
      class="records-table"
    >
      <el-table-column type="index" label="#" width="60" align="center" />

      <el-table-column label="用户信息" width="160" fixed="left">
        <template #default="{ row }">
          <div class="user-info">
            <strong>{{ row.user_info?.username || '-' }}</strong>
            <el-tag size="small" :type="getRoleType(row.user_info?.role)">
              {{ getRoleLabel(row.user_info?.role) }}
            </el-tag>
          </div>
        </template>
      </el-table-column>

      <el-table-column label="场景/主题" min-width="220" show-overflow-tooltip>
        <template #default="{ row }">
          <div class="scenario-info">
            <span v-if="row.scenario_info" class="scenario-name">
              {{ row.scenario_info.icon }} {{ row.scenario_info.title }}
            </span>
            <span v-else class="text-muted">未知场景</span>
            
            <el-tag
              v-if="row.topic_info"
              size="small"
              type="info"
              effect="plain"
              style="margin-top: 4px;"
            >
              主题{{ row.topic_info.topic_number }}: {{ row.topic_info.title }}
            </el-tag>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="overall_score" label="得分" width="120" align="center" sortable>
        <template #default="{ row }">
          <div class="score-cell" :class="getScoreClass(row.overall_score)">
            <span class="score-value">{{ row.overall_score }}</span>
            <el-tag
              size="small"
              :type="getScoreLevelType(row.score_level)"
              effect="dark"
              round
            >
              {{ getScoreLevelLabel(row.score_level) }}
            </el-tag>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="duration_seconds" label="用时" width="100" align="center">
        <template #default="{ row }">
          {{ row.formatted_duration || '-' }}
        </template>
      </el-table-column>

      <el-table-column prop="is_completed" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_completed ? 'success' : 'warning'" size="small">
            {{ row.is_completed ? '已完成' : '进行中' }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="created_at" label="提交时间" width="170" sortable>
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>

      <el-table-column label="操作" width="150" fixed="right" align="center">
        <template #default="{ row }">
          <el-button text type="primary" size="small" @click.stop="handleViewDetail(row)">详情</el-button>
          <el-popconfirm
            title="确定删除此记录？"
            confirm-button-text="确定"
            cancel-button-text="取消"
            @confirm="handleDelete(row)"
          >
            <template #reference>
              <el-button text type="danger" size="small" @click.stop>删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>

    <!-- 详情抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      :title="'练习详情 - #' + currentRecord?.id"
      size="700px"
      direction="rtl"
    >
      <div v-loading="detailLoading" class="detail-container">
        <template v-if="currentRecord">
        <div class="detail-content">
          <!-- 基本信息 -->
          <el-descriptions title="基本信息" :column="2" border>
            <el-descriptions-item label="用户">
              <div class="user-detail">
                <strong>{{ currentRecord.user_info?.username }}</strong>
                <el-tag size="small">{{ getRoleLabel(currentRecord.user_info?.role) }}</el-tag>
              </div>
            </el-descriptions-item>
            
            <el-descriptions-item label="场景">
              <span v-if="currentRecord.scenario_info">
                {{ currentRecord.scenario_info.icon }} {{ currentRecord.scenario_info.title }}
              </span>
              <span v-else>-</span>
            </el-descriptions-item>
            
            <el-descriptions-item label="主题">
              <span v-if="currentRecord.topic_info">
                主题{{ currentRecord.topic_info.topic_number }}: {{ currentRecord.topic_info.title }}
              </span>
              <span v-else>-</span>
            </el-descriptions-item>
            
            <el-descriptions-item label="综合得分">
              <div class="score-display" :class="getScoreClass(currentRecord.overall_score)">
                <span class="score-big">{{ currentRecord.overall_score }}</span>
                <el-tag :type="getScoreLevelType(currentRecord.score_level)" effect="dark">
                  {{ getScoreLevelLabel(currentRecord.score_level) }}
                </el-tag>
              </div>
            </el-descriptions-item>
            
            <el-descriptions-item label="用时">
              {{ currentRecord.formatted_duration || '-' }}
            </el-descriptions-item>
            
            <el-descriptions-item label="状态">
              <el-tag :type="currentRecord.is_completed ? 'success' : 'warning'">
                {{ currentRecord.is_completed ? '已完成' : '进行中' }}
              </el-tag>
            </el-descriptions-item>
            
            <el-descriptions-item label="创建时间" :span="2">
              {{ formatDate(currentRecord.created_at) }}
            </el-descriptions-item>
          </el-descriptions>

          <!-- 提示词内容 -->
          <el-divider content-position="left">提示词内容</el-divider>
          
          <el-card shadow="never" class="content-card">
            <template #header>
              <span>用户提示词</span>
            </template>
            <div class="prompt-content">{{ currentRecord.user_prompt }}</div>
          </el-card>

          <el-card v-if="currentRecord.llm_response" shadow="never" class="content-card" style="margin-top: 16px;">
            <template #header>
              <span>模型回复</span>
            </template>
            <div class="response-content">{{ currentRecord.llm_response }}</div>
          </el-card>

          <!-- 评分明细 -->
          <el-divider content-position="left">评分明细</el-divider>
          
          <el-card v-if="currentRecord.scores && Object.keys(currentRecord.scores).length" shadow="never">
            <pre class="scores-json">{{ JSON.stringify(currentRecord.scores, null, 2) }}</pre>
          </el-card>
          <el-empty v-else description="暂无详细评分数据" :image-size="80" />

          <!-- 建议 -->
          <el-divider content-position="left">修改建议</el-divider>
          
          <el-card v-if="currentRecord.suggestions" shadow="never" class="content-card">
            <div class="suggestions-content">{{ currentRecord.suggestions }}</div>
          </el-card>
          <el-empty v-else description="暂无修改建议" :image-size="80" />

          <!-- 反馈 -->
          <el-divider content-position="left">学生反馈</el-divider>
          
          <el-card v-if="currentRecord.feedback" shadow="never" class="content-card">
            <div class="feedback-content">{{ currentRecord.feedback }}</div>
          </el-card>
          <el-empty v-else description="暂无反馈" :image-size="80" />
        </div>
      </template>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Download, Document, CircleCheck, TrendCharts, Timer,
  ArrowDown, ArrowUp, Search, Refresh
} from '@element-plus/icons-vue'
import { getRecordList, getScenarioList, getPracticeStatistics, getRecordDetail } from '@/api/practice'

const loading = ref(false)
const records = ref([])
const scenarios = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const showAdvancedFilters = ref(false)
const drawerVisible = ref(false)
const currentRecord = ref(null)
const detailLoading = ref(false)

const statistics = reactive({
  total: 0,
  completed: 0,
  avg_score: 0,
  total_duration: 0
})

const filters = reactive({
  keyword: '',
  user: '',
  scenario: null,
  score_level: '',
  is_completed: '',
  score_min: null,
  score_max: null,
})

const dateRange = ref(null)

onMounted(async () => {
  await Promise.all([
    loadScenarios(),
    loadStatistics(),
    loadData()
  ])
})

async function loadScenarios() {
  try {
    const res = await getScenarioList({ page_size: 100 })
    if (res.code === 200) {
      scenarios.value = res.data.results || res.data
    }
  } catch (error) {
    console.error('加载场景列表失败:', error)
  }
}

async function loadStatistics() {
  try {
    const res = await getPracticeStatistics()
    if (res.code === 200 && res.data?.overview) {
      Object.assign(statistics, res.data.overview)
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

async function loadData() {
  loading.value = true
  
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    if (filters.keyword) params.search = filters.keyword
    if (filters.user) params.user = filters.user
    if (filters.scenario) params.scenario = filters.scenario
    if (filters.score_level) params.score_level = filters.score_level
    if (filters.is_completed !== '') params.is_completed = filters.is_completed
    if (filters.score_min !== null) params.score_min = filters.score_min
    if (filters.score_max !== null) params.score_max = filters.score_max
    
    if (dateRange.value?.length === 2) {
      params.date_from = dateRange.value[0]
      params.date_to = dateRange.value[1]
    }
    
    const res = await getRecordList(params)
    
    if (res.code === 200) {
      records.value = res.data.results || []
      total.value = res.data.count || records.value.length
    }
  } catch (error) {
    console.error('加载记录失败:', error)
  } finally {
    loading.value = false
  }
}

function toggleFilters() {
  showAdvancedFilters.value = !showAdvancedFilters.value
}

function resetFilters() {
  Object.assign(filters, {
    keyword: '',
    user: '',
    scenario: null,
    score_level: '',
    is_completed: '',
    score_min: null,
    score_max: null,
  })
  dateRange.value = null
  currentPage.value = 1
  loadData()
}

async function handleViewDetail(record) {
  drawerVisible.value = true
  detailLoading.value = true
  currentRecord.value = null
  
  try {
    const res = await getRecordDetail(record.id)
    if (res.code === 200) {
      currentRecord.value = res.data
    } else {
      currentRecord.value = record
    }
  } catch (error) {
    console.error('加载详情失败:', error)
    currentRecord.value = record
  } finally {
    detailLoading.value = false
  }
}

async function handleDelete(record) {
  try {
    await deleteRecord(record.id)
    ElMessage.success('删除成功')
    loadData()
    loadStatistics()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

async function handleExport() {
  try {
    const format = await ElMessageBox.confirm(
      '请选择导出格式',
      '导出数据',
      {
        confirmButtonText: 'Excel',
        cancelButtonText: 'JSON',
        distinguishCancelAndClose: true,
        type: 'info'
      }
    ).then(() => 'excel').catch((action) => action === 'cancel' ? 'json' : null)
    
    if (!format) return

    const res = await exportRecords({ format })
    
    if (format === 'excel') {
      const blob = new Blob([res], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `practice_records_${new Date().toISOString().split('T')[0]}.xlsx`
      link.click()
      window.URL.revokeObjectURL(url)
    }
    
    ElMessage.success(`成功导出 ${res.data?.length || 0} 条记录`)
  } catch (error) {
    console.error('导出失败:', error)
  }
}

function getScoreClass(score) {
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 70) return 'average'
  if (score >= 60) return 'needs-improvement'
  return 'poor'
}

function getScoreLevelType(level) {
  const map = {
    excellent: 'success',
    good: 'success',
    average: 'warning',
    needs_improvement: 'danger',
    poor: 'danger'
  }
  return map[level] || 'info'
}

function getScoreLevelLabel(level) {
  const map = {
    excellent: '优秀',
    good: '良好',
    average: '中等',
    needs_improvement: '待提高',
    poor: '较差'
  }
  return map[level] || level
}

function getRoleType(role) {
  const map = { admin: 'danger', teacher: 'warning', student: '' }
  return map[role] || 'info'
}

function getRoleLabel(role) {
  const map = { admin: '管理员', teacher: '教师', student: '学生' }
  return map[role] || role
}

function formatDuration(seconds) {
  if (!seconds) return '-'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  
  if (hours > 0) {
    return `${hours}时${minutes}分`
  } else if (minutes > 0) {
    return `${minutes}分${secs}秒`
  }
  return `${secs}秒`
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.records-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  font-size: 22px;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  overflow: hidden;
}

.stat-card .stat-content {
  position: relative;
  z-index: 1;
}

.stat-card .stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-card .stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.stat-card .stat-icon {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 48px;
  opacity: 0.1;
}

.stat-card.success .stat-icon { color: #67c23a; }
.stat-card.warning .stat-icon { color: #e6a23c; }
.stat-card.danger .stat-icon { color: #f56c6c; }

.filter-card {
  margin-bottom: 24px;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.records-table {
  background: #fff;
  border-radius: 8px;
}

.records-table :deep(.el-table__row) {
  cursor: pointer;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  line-height: 1.4;
}

.scenario-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.scenario-name {
  font-weight: 500;
}

.text-muted {
  color: #c0c4cc;
}

.score-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.score-value {
  font-size: 22px;
  font-weight: 700;
}

.score-cell.excellent .score-value { color: #67c23a; }
.score-cell.good .score-value { color: #409eff; }
.score-cell.average .score-value { color: #e6a23c; }
.score-cell.needs-improvement .score-value { color: #f56c6c; }
.score-cell.poor .score-value { color: #f56c6c; }

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding: 16px 0;
}

.detail-content {
  padding: 0 20px;
}

.user-detail {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-big {
  font-size: 36px;
  font-weight: 700;
}

.score-display.excellent .score-big { color: #67c23a; }
.score-display.good .score-big { color: #409eff; }
.score-display.average .score-big { color: #e6a23c; }
.score-display.needs-improvement .score-big { color: #f56c6c; }
.score-display.poor .score-big { color: #f56c6c; }

.content-card {
  margin-bottom: 16px;
}

.prompt-content,
.response-content,
.suggestions-content,
.feedback-content {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.8;
  font-size: 14px;
  color: #303133;
  max-height: 300px;
  overflow-y: auto;
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
}

.scores-json {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 6px;
  font-size: 13px;
  overflow-x: auto;
  max-height: 300px;
}
</style>
