<template>
  <div class="student-detail-container" v-loading="loading">
    <!-- 顶部导航 -->
    <div class="page-header">
      <el-button text @click="$router.push('/teacher/workspace')">
        ← 返回工作台
      </el-button>
      <h2>学生详情：{{ detail.basic?.real_name }} ({{ detail.basic?.student_id }})</h2>
    </div>

    <div v-if="!loading && detail.basic">
      <el-row :gutter="20">
        <!-- 左侧：基本信息 + 统计面板 -->
        <el-col :span="8">
          <el-card shadow="hover" class="info-card">
            <div class="profile-section">
              <el-avatar :size="64" :src="detail.basic.avatar">
                {{ (detail.basic.real_name || '?').charAt(0) }}
              </el-avatar>
              <div class="profile-info">
                <h3>{{ detail.basic.real_name }}</h3>
                <p>学号：{{ detail.basic.student_id || '-' }}</p>
                <p>班级：{{ detail.basic.class_name || '-' }}</p>
                <p>注册：{{ formatDate(detail.basic.date_joined) }}</p>
                <el-tag :type="statusTagType(detail.basic.status)" size="small">
                  {{ statusLabel(detail.basic.status) }}
                </el-tag>
              </div>
            </div>
          </el-card>

          <el-card shadow="hover" class="stats-card" style="margin-top: 16px;">
            <template #header><span>📊 个人统计</span></template>
            <div class="stat-grid">
              <div class="stat-item">
                <div class="stat-val">{{ detail.stats?.practice_count }}</div>
                <div class="stat-lbl">练习次数</div>
              </div>
              <div class="stat-item">
                <div class="stat-val">{{ detail.stats?.avg_score }}</div>
                <div class="stat-lbl">平均分</div>
              </div>
              <div class="stat-item">
                <div class="stat-val">{{ detail.stats?.max_score }}</div>
                <div class="stat-lbl">最高分</div>
              </div>
              <div class="stat-item">
                <div class="stat-val">{{ detail.stats?.completion_rate }}%</div>
                <div class="stat-lbl">完成率</div>
              </div>
              <div class="stat-item">
                <div class="stat-val">{{ detail.stats?.active_days }}</div>
                <div class="stat-lbl">活跃天数</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧：成绩趋势图 -->
        <el-col :span="16">
          <el-card shadow="hover">
            <LineChart
              title="📈 成绩趋势（近30天）"
              :x-axis-data="trendDates"
              :series-data="trendScores"
              :smooth="true"
              height="360px"
            />
          </el-card>
        </el-col>
      </el-row>

      <!-- 练习记录明细表 -->
      <el-card shadow="hover" style="margin-top: 20px;">
        <template #header>
          <span>📋 练习记录明细</span>
          <el-select v-model="recordPeriod" size="small" style="float: right; width: 120px;" @change="fetchDetail">
            <el-option label="近7天" value="7d" />
            <el-option label="近30天" value="30d" />
            <el-option label="近90天" value="90d" />
          </el-select>
        </template>
        <el-table :data="detail.practice_records || []" stripe>
          <el-table-column prop="scenario_title" label="场景" min-width="140" />
          <el-table-column prop="topic_title" label="主题" min-width="160" />
          <el-table-column prop="overall_score" label="得分" width="80">
            <template #default="{ row }">
              <el-tag :type="scoreTagType(row.overall_score)" size="small">
                {{ row.overall_score }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="耗时" width="90">
            <template #default="{ row }">
              {{ formatDuration(row.duration_seconds) }}
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="日期" width="160" />
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import LineChart from '@/components/charts/LineChart.vue'
import { getStudentDetail } from '@/api/teacher'

const route = useRoute()
const loading = ref(false)
const detail = ref({})
const recordPeriod = ref('30d')

const studentId = computed(() => route.params.id)

const trendDates = computed(() =>
  (detail.value.score_trend || []).map(t => t.date)
)
const trendScores = computed(() =>
  (detail.value.score_trend || []).map(t => t.avg_score)
)

function scoreTagType(score) {
  if (score >= 90) return 'success'
  if (score >= 80) return ''
  if (score >= 60) return 'warning'
  return 'danger'
}

function statusTagType(status) {
  const map = { excellent: 'success', normal: '', attention: 'warning' }
  return map[status] || 'info'
}

function statusLabel(status) {
  const map = { excellent: '🏆 优秀', normal: '✅ 正常', attention: '⚠️ 需关注' }
  return map[status] || '-'
}

function formatDate(isoStr) {
  if (!isoStr) return '-'
  return new Date(isoStr).toLocaleDateString()
}

function formatDuration(seconds) {
  if (!seconds) return '-'
  if (seconds < 60) return `${seconds}秒`
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return s ? `${m}分${s}秒` : `${m}分钟`
}

async function fetchDetail() {
  loading.value = true
  try {
    const res = await getStudentDetail(studentId.value, { period: recordPeriod.value })
    if (res.code === 200) {
      detail.value = res.data
    }
  } catch (e) {
    console.error('加载学生详情失败:', e)
  } finally {
    loading.value = false
  }
}

watch(recordPeriod, fetchDetail)

onMounted(fetchDetail)
</script>

<style scoped lang="scss">
.student-detail-container {
  .page-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;

    h2 {
      margin: 0;
      font-size: 20px;
      color: #303133;
    }
  }

  .info-card {
    border-radius: 8px;

    .profile-section {
      display: flex;
      gap: 16px;
      align-items: flex-start;

      .profile-info {
        h3 { margin: 0 0 8px; color: #303133; }
        p { margin: 2px 0; font-size: 13px; color: #606266; }
      }
    }
  }

  .stats-card {
    border-radius: 8px;

    .stat-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;

      .stat-item {
        text-align: center;
        padding: 8px;
        background: #f5f7fa;
        border-radius: 6px;

        .stat-val { font-size: 20px; font-weight: bold; color: #303133; }
        .stat-lbl { font-size: 12px; color: #909399; margin-top: 2px; }
      }
    }
  }
}
</style>
