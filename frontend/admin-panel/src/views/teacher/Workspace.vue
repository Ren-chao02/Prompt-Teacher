<template>
  <div class="workspace-container">
    <!-- A区：顶部操作栏 -->
    <div class="page-header">
      <h2>📋 我的工作台</h2>
      <div class="header-actions">
        <el-select
          v-if="myClasses.length > 0"
          v-model="selectedClassId"
          placeholder="全部班级"
          clearable
          style="width: 180px; margin-right: 10px;"
          @change="fetchData"
        >
          <el-option
            v-for="cls in myClasses"
            :key="cls.id"
            :label="`${cls.name} (${cls.student_count}人)`"
            :value="cls.id"
          />
        </el-select>
        <el-select v-model="period" style="width: 130px; margin-right: 10px;" @change="fetchData">
          <el-option label="最近7天" value="7d" />
          <el-option label="最近30天" value="30d" />
          <el-option label="最近90天" value="90d" />
        </el-select>
        <el-button type="primary" plain disabled>
          📥 导出报告
        </el-button>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-if="!loading && workspaceData.students && workspaceData.students.length === 0"
      description="您暂未管理任何班级和学生"
      :image-size="120"
    >
      <el-button type="primary">联系管理员分配班级</el-button>
    </el-empty>

    <div v-else v-loading="loading">
      <!-- B区：班级统计卡片 -->
      <el-row :gutter="16" class="stat-row">
        <el-col :span="4" v-for="(card, idx) in statCards" :key="idx">
          <el-card shadow="hover" class="stat-card" :style="{ borderTop: `3px solid ${card.color}` }">
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-label">{{ card.label }}</div>
          </el-card>
        </el-col>
      </el-row>

      <!-- C区：学生总览表 -->
      <el-card shadow="hover" class="table-card" style="margin-top: 20px;">
        <template #header>
          <span>📋 学生完成情况</span>
        </template>

        <el-table
          :data="workspaceData.students || []"
          stripe
          style="width: 100%"
          :default-sort="{ prop: 'avg_score', order: 'descending' }"
        >
          <el-table-column type="index" label="#" width="50" />
          <el-table-column prop="real_name" label="姓名" width="100" sortable />
          <el-table-column prop="student_id" label="学号" width="120" sortable />
          <el-table-column label="资料完成度" width="150" sortable :sort-method="(a, b) => (a.completion_rate || 0) - (b.completion_rate || 0)">
            <template #default="{ row }">
              <el-progress :percentage="row.completion_rate || 0" :stroke-width="8" />
            </template>
          </el-table-column>
          <el-table-column prop="practice_count" label="练习次数" width="100" sortable sort-by="practice_count" />
          <el-table-column prop="avg_score" label="练习均分" width="110" sortable>
            <template #default="{ row }">
              <el-tag :type="scoreTagType(row.avg_score)" size="small">
                {{ row.avg_score ?? '-' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="最近登录" width="130" sortable prop="last_login">
            <template #default="{ row }">
              {{ formatRelativeTime(row.last_login) }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <span>{{ statusLabel(row.status) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="goDetail(row)">
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- D区：趋势图表 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card shadow="hover">
            <PieChart
              title="📊 班级成绩分布"
              :data="pieData"
              height="320px"
            />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <LineChart
              title="📈 近30天活跃度趋势"
              :x-axis-data="trendDates"
              :series-data="trendActiveStudents"
              :show-area="true"
              height="320px"
            />
          </el-card>
        </el-col>
      </el-row>

      <!-- E区：预警提醒区 -->
      <el-card v-if="workspaceData.alerts && workspaceData.alerts.length > 0" shadow="hover" class="alert-card" style="margin-top: 20px;">
        <template #header>
          <span>⚠️ 需要关注的学生 ({{ workspaceData.alerts.length }}人)</span>
        </template>
        <div class="alert-list">
          <div
            v-for="(alert, idx) in workspaceData.alerts"
            :key="idx"
            class="alert-item"
          >
            <div class="alert-main">
              <strong>{{ alert.student_name }}</strong>
              <span class="alert-detail">{{ alert.detail }}</span>
            </div>
            <div class="alert-actions">
              <el-button link type="primary" size="small" @click="goDetailById(alert.student_id)">
                查看
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PieChart from '@/components/charts/PieChart.vue'
import LineChart from '@/components/charts/LineChart.vue'
import { getWorkspaceData } from '@/api/teacher'
import { getMyClasses } from '@/api/auth'

const router = useRouter()

const loading = ref(false)
const period = ref('30d')
const selectedClassId = ref(null)
const myClasses = ref([])
const workspaceData = ref({})

// B区：统计卡片
const statCards = computed(() => {
  const s = workspaceData.value.stats || {}
  return [
    { label: '班级人数', value: s.total_students ?? '-', color: '#409EFF' },
    { label: '班级均分', value: s.class_avg_score ?? '-', color: '#67C23A' },
    { label: '资料完成率', value: `${s.material_completion_rate ?? 0}%`, color: '#E6A23C' },
    { label: '活跃率', value: `${s.active_rate ?? 0}%`, color: '#67C23A' },
    { label: '练习次数', value: s.total_practices ?? '-', color: '#F56C6C' },
    { label: '待关注', value: s.attention_count ?? 0, color: '#E6A23C' },
  ]
})

// D区：饼图数据
const pieData = computed(() => {
  const d = workspaceData.value.charts?.score_distribution || {}
  const labels = { excellent: '优秀(≥90)', good: '良好(80-89)', average: '中等(70-79)', pass: '及格(60-69)', fail: '不及格(<60)' }
  return Object.entries(d)
    .filter(([, v]) => v > 0)
    .map(([key, val]) => ({ name: labels[key] || key, value: val }))
})

// D区：折线图数据
const trendDates = computed(() =>
  (workspaceData.value.charts?.activity_trend || []).map(d => d.date)
)
const trendActiveStudents = computed(() =>
  (workspaceData.value.charts?.activity_trend || []).map(d => d.active_students || 0)
)

// 辅助方法
function scoreTagType(score) {
  if ((score !== 0 && !score)) return 'info'
  if (score >= 90) return 'success'
  if (score >= 80) return ''
  if (score >= 60) return 'warning'
  return 'danger'
}

function statusLabel(status) {
  const map = { excellent: '🏆 优秀', normal: '✅ 正常', attention: '⚠️ 需关注' }
  return map[status] || '-'
}

function formatRelativeTime(isoStr) {
  if (!isoStr) return '-'
  const diff = Date.now() - new Date(isoStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${mins}分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}天前`
  return new Date(isoStr).toLocaleDateString()
}

function goDetail(row) {
  router.push(`/teacher/student/${row.id}?period=${period.value}`)
}

function goDetailById(id) {
  router.push(`/teacher/student/${id}?period=${period.value}`)
}

// 数据加载
async function fetchData() {
  loading.value = true
  try {
    const params = { period: period.value }
    if (selectedClassId.value) params.class_id = selectedClassId.value
    const res = await getWorkspaceData(params)
    if (res.code === 200) {
      workspaceData.value = res.data
    }
  } catch (e) {
    console.error('加载工作台数据失败:', e)
  } finally {
    loading.value = false
  }
}

async function loadMyClasses() {
  try {
    const res = await getMyClasses()
    if (res.code === 200) myClasses.value = res.data || []
  } catch (e) { /* silent */ }
}

onMounted(async () => {
  await loadMyClasses()
  fetchData()
})
</script>

<style scoped lang="scss">
.workspace-container {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h2 {
      margin: 0;
      font-size: 22px;
      color: #303133;
    }

    .header-actions {
      display: flex;
      align-items: center;
    }
  }

  .stat-row {
    .stat-card {
      text-align: center;
      border-radius: 8px;

      .stat-value {
        font-size: 28px;
        font-weight: bold;
        color: #303133;
        margin-bottom: 4px;
      }

      .stat-label {
        font-size: 13px;
        color: #909399;
      }
    }
  }

  .table-card {
    border-radius: 8px;
  }

  .alert-card {
    border-radius: 8px;
    border-left: 4px solid #E6A23C;

    .alert-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .alert-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      background: #fdf6ec;
      border-radius: 6px;

      .alert-main {
        display: flex;
        gap: 12px;
        align-items: baseline;

        strong { color: #303133; }
        .alert-detail { color: #E6A23C; font-size: 13px; }
      }
    }
  }
}
</style>
