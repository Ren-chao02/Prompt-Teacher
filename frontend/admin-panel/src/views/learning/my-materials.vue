<template>
  <div class="my-materials-container">
    <!-- 顶部统计卡 -->
    <el-row :gutter="16" class="stats-row" v-loading="loading">
      <el-col :xs="12" :sm="6" v-for="stat in statsCards" :key="stat.key">
        <div class="stat-card" :style="{ '--c': stat.color }">
          <div class="stat-icon">
            <el-icon><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 主体内容 -->
    <el-card shadow="never" class="main-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="title">我创建的内容</span>
            <span class="subtitle">管理和查看自己创作的学习资料</span>
          </div>
          <div class="header-right">
            <el-button type="primary" :icon="Plus" @click="$router.push('/learning/create')">
              创建新内容
            </el-button>
          </div>
        </div>
      </template>

      <!-- 筛选/搜索 -->
      <div class="filter-bar">
        <el-input
          v-model="searchForm.search"
          placeholder="搜索我的内容标题..."
          :prefix-icon="Search"
          clearable
          class="search-input"
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
        <el-select v-model="searchForm.category" placeholder="全部分类" clearable class="filter-select" @change="handleSearch">
          <el-option label="全部" value="" />
          <el-option label="基础入门" value="basic" />
          <el-option label="进阶技巧" value="intermediate" />
          <el-option label="高级应用" value="advanced" />
          <el-option label="最佳实践" value="best_practices" />
        </el-select>
        <el-select v-model="searchForm.status" placeholder="全部状态" clearable class="filter-select" @change="handleSearch">
          <el-option label="全部" value="" />
          <el-option label="草稿" value="draft" />
          <el-option label="已发布" value="published" />
          <el-option label="已下架" value="archived" />
        </el-select>
        <el-button type="primary" plain @click="handleSearch">查询</el-button>
      </div>

      <!-- 视图切换 -->
      <div class="view-toolbar">
        <el-radio-group v-model="viewMode" size="small">
          <el-radio-button label="card">
            <el-icon><Grid /></el-icon>卡片
          </el-radio-button>
          <el-radio-button label="table">
            <el-icon><List /></el-icon>表格
          </el-radio-button>
        </el-radio-group>
        <span class="total-tip">共 {{ totalCount }} 项</span>
      </div>

      <!-- 卡片视图 -->
      <transition name="fade-mode" mode="out-in">
        <div v-if="viewMode === 'card'" key="card" v-loading="loading" class="card-list">
          <el-empty v-if="!tableData.length" description="还没有创建过内容" />
          <div
            v-for="item in tableData"
            :key="item.id"
            class="material-item"
          >
            <div class="item-cover" :style="getCoverStyle(item)">
              <el-icon><Document /></el-icon>
            </div>
            <div class="item-main">
              <div class="item-title-row">
                <span class="item-title" @click="goDetail(item)">{{ item.title }}</span>
                <el-tag size="small" :type="getStatusTagType(item.status)">
                  {{ item.status_display || getStatusLabel(item.status) }}
                </el-tag>
              </div>
              <p class="item-summary">{{ item.summary || '暂无摘要' }}</p>
              <div class="item-tags" v-if="item.tags && item.tags.length">
                <el-tag
                  v-for="t in item.tags.slice(0, 4)"
                  :key="t"
                  size="small"
                  effect="plain"
                  type="info"
                >#{{ t }}</el-tag>
              </div>
              <div class="item-meta">
                <span class="meta-item">
                  <el-icon><View /></el-icon>{{ formatNumber(item.view_count) }} 阅读
                </span>
                <span class="meta-item">
                  <el-icon><Star /></el-icon>{{ formatNumber(item.like_count) }} 点赞
                </span>
                <span class="meta-item">
                  <el-icon><Clock /></el-icon>{{ formatDate(item.updated_at) }}
                </span>
              </div>
            </div>
            <div class="item-actions">
              <el-button
                size="small"
                :icon="View"
                @click="goDetail(item)"
              >查看</el-button>
              <el-button
                size="small"
                type="primary"
                :icon="EditPen"
                @click="goEdit(item)"
              >编辑</el-button>
              <el-dropdown trigger="click">
                <el-button size="small" :icon="MoreFilled" />
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item
                      v-if="item.status !== 'published'"
                      @click="handleToggleStatus(item, 'publish')"
                    >
                      <el-icon><Promotion /></el-icon>发布
                    </el-dropdown-item>
                    <el-dropdown-item
                      v-else
                      @click="handleToggleStatus(item, 'archive')"
                    >
                      <el-icon><Box /></el-icon>下架
                    </el-dropdown-item>
                    <el-dropdown-item divided @click="handleDelete(item)">
                      <span style="color:#EF4444">
                        <el-icon><Delete /></el-icon>删除
                      </span>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>

        <div v-else key="table" v-loading="loading" class="table-wrap">
          <el-empty v-if="!tableData.length" description="还没有创建过内容" />
          <el-table
            v-else
            :data="tableData"
            :header-cell-style="{ background: '#F9FAFB', color: '#374151', fontWeight: 600 }"
            stripe
            @row-click="goDetail"
          >
            <el-table-column prop="title" label="标题" min-width="240">
              <template #default="{ row }">
                <span class="row-title">{{ row.title }}</span>
              </template>
            </el-table-column>
            <el-table-column label="分类" width="110">
              <template #default="{ row }">
                <el-tag size="small" :type="getCategoryTagType(row.category)" effect="light">
                  {{ row.category_display || getCategoryLabel(row.category) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag size="small" :type="getStatusTagType(row.status)">
                  {{ row.status_display || getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="阅读" width="90" align="center">
              <template #default="{ row }">
                <span class="num-cell">{{ formatNumber(row.view_count) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="点赞" width="90" align="center">
              <template #default="{ row }">
                <span class="num-cell">{{ formatNumber(row.like_count) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="收藏" width="90" align="center">
              <template #default="{ row }">
                <span class="num-cell">{{ formatNumber(row.favorite_count) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="更新时间" width="170">
              <template #default="{ row }">
                <span class="time-cell">{{ formatDate(row.updated_at) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="{ row }">
                <el-button size="small" link type="primary" @click.stop="goDetail(row)">查看</el-button>
                <el-button size="small" link type="primary" @click.stop="goEdit(row)">编辑</el-button>
                <el-button
                  size="small"
                  link
                  :type="row.status === 'published' ? 'warning' : 'success'"
                  @click.stop="handleToggleStatus(row, row.status === 'published' ? 'archive' : 'publish')"
                >
                  {{ row.status === 'published' ? '下架' : '发布' }}
                </el-button>
                <el-button size="small" link type="danger" @click.stop="handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </transition>

      <!-- 分页 -->
      <div class="pagination-wrap" v-if="totalCount > 0">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="totalCount"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="fetchList"
          @current-change="fetchList"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Grid,
  List,
  Document,
  View,
  Star,
  Clock,
  EditPen,
  MoreFilled,
  Delete,
  Promotion,
  Box,
  Edit,
  ChatLineRound,
  Cpu,
  Trophy
} from '@element-plus/icons-vue'
import {
  getMyMaterials,
  getStatistics,
  publishMaterial,
  archiveMaterial,
  deleteMaterial
} from '@/api/learning'

const router = useRouter()

const loading = ref(false)
const tableData = ref([])
const totalCount = ref(0)
const page = ref(1)
const pageSize = ref(10)
const viewMode = ref(localStorage.getItem('myMaterialsView') || 'card')
const stats = ref({
  total: 0, published: 0, draft: 0, archived: 0,
  total_views: 0, total_likes: 0, total_favorites: 0
})

const searchForm = reactive({
  search: '',
  category: '',
  status: ''
})

const statsCards = computed(() => [
  { key: 'total', label: '总内容', value: stats.value.total, icon: Document, color: '#3B82F6' },
  { key: 'published', label: '已发布', value: stats.value.published, icon: Promotion, color: '#10B981' },
  { key: 'total_views', label: '总阅读', value: formatNumber(stats.value.total_views), icon: View, color: '#F59E0B' },
  { key: 'total_likes', label: '总点赞', value: formatNumber(stats.value.total_likes), icon: Star, color: '#EC4899' }
])

onMounted(() => {
  fetchList()
  fetchStats()
})

watch(viewMode, (v) => localStorage.setItem('myMaterialsView', v))

async function fetchList() {
  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
      search: searchForm.search || undefined,
      category: searchForm.category || undefined,
      status: searchForm.status || undefined,
      ordering: '-updated_at'
    }
    const res = await getMyMaterials(params)
    const data = res.data.data || res.data
    if (data.results !== undefined) {
      tableData.value = data.results
      totalCount.value = data.count
    } else if (Array.isArray(data)) {
      tableData.value = data
      totalCount.value = data.length
    } else {
      tableData.value = []
      totalCount.value = 0
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function fetchStats() {
  try {
    const res = await getStatistics()
    const d = res.data.data || res.data
    stats.value = {
      total: d.total ?? 0,
      published: d.published ?? 0,
      draft: d.draft ?? 0,
      archived: d.archived ?? 0,
      total_views: d.total_views ?? 0,
      total_likes: d.total_likes ?? 0,
      total_favorites: d.total_favorites ?? 0
    }
  } catch (e) {
    /* 静默 */
  }
}

function handleSearch() {
  page.value = 1
  fetchList()
}

function goDetail(row) {
  router.push(`/learning/detail/${row.id}`)
}

function goEdit(row) {
  router.push(`/learning/edit/${row.id}`)
}

async function handleToggleStatus(row, type) {
  const isPublish = type === 'publish'
  try {
    await ElMessageBox.confirm(
      `确定要${isPublish ? '发布' : '下架'}《${row.title}》吗？`,
      '确认操作',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    if (isPublish) {
      await publishMaterial(row.id)
    } else {
      await archiveMaterial(row.id)
    }
    ElMessage.success(isPublish ? '已发布' : '已下架')
    fetchList()
    fetchStats()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除《${row.title}》吗？此操作不可恢复！`,
      '警告',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    await deleteMaterial(row.id)
    ElMessage.success('已删除')
    fetchList()
    fetchStats()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

function getCoverStyle(item) {
  const map = {
    basic: 'linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%)',
    intermediate: 'linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%)',
    advanced: 'linear-gradient(135deg, #EF4444 0%, #F87171 100%)',
    best_practices: 'linear-gradient(135deg, #10B981 0%, #6EE7B7 100%)'
  }
  return { background: map[item.category] || map.basic }
}

function getCategoryTagType(c) {
  return { basic: 'primary', intermediate: 'warning', advanced: 'danger', best_practices: 'success' }[c] || 'info'
}
function getStatusTagType(s) {
  return { draft: 'info', published: 'success', archived: 'danger' }[s] || 'info'
}
function getCategoryLabel(c) {
  return { basic: '基础入门', intermediate: '进阶技巧', advanced: '高级应用', best_practices: '最佳实践' }[c] || c
}
function getStatusLabel(s) {
  return { draft: '草稿', published: '已发布', archived: '已下架' }[s] || s
}
function formatNumber(n) {
  if (!n) return '0'
  if (n >= 10000) return (n / 10000).toFixed(1) + 'w'
  return String(n)
}
function formatDate(s) {
  if (!s) return '-'
  const d = new Date(s)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}
</script>

<style scoped>
.my-materials-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-row {
  margin-bottom: 4px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid #F3F4F6;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: all 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: color-mix(in srgb, var(--c) 12%, transparent);
  color: var(--c);
  font-size: 24px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: #6B7280;
  margin-top: 2px;
}

.main-card {
  border-radius: 14px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left .title {
  font-size: 17px;
  font-weight: 600;
  color: #111827;
  display: block;
  margin-bottom: 2px;
}

.header-left .subtitle {
  font-size: 13px;
  color: #6B7280;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}

.search-input {
  width: 280px;
}

.filter-select {
  width: 160px;
}

.view-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.total-tip {
  font-size: 13px;
  color: #6B7280;
}

/* 卡片列表 */
.card-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.material-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #FAFAFA;
  border: 1px solid #F3F4F6;
  border-radius: 12px;
  transition: all 0.2s;
}

.material-item:hover {
  background: #ffffff;
  border-color: #DBEAFE;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.08);
}

.item-cover {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  color: #ffffff;
  font-size: 32px;
  flex-shrink: 0;
}

.item-main {
  flex: 1;
  min-width: 0;
}

.item-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.item-title {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
  cursor: pointer;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-title:hover {
  color: #2563EB;
}

.item-summary {
  font-size: 13px;
  color: #6B7280;
  margin: 0 0 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.item-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #9CA3AF;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.item-actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-end;
}

.table-wrap {
  border-radius: 8px;
  overflow: hidden;
}

.row-title {
  font-weight: 500;
  color: #111827;
}

.num-cell {
  font-weight: 600;
  color: #111827;
}

.time-cell {
  font-size: 13px;
  color: #6B7280;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

.fade-mode-enter-active,
.fade-mode-leave-active {
  transition: opacity 0.2s;
}
.fade-mode-enter-from,
.fade-mode-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .filter-bar { flex-direction: column; }
  .search-input, .filter-select { width: 100%; }
  .item-actions { flex-direction: row; }
}
</style>
