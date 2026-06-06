<template>
  <div class="learning-list-container">
    <!-- 顶部欢迎 / 数据概览 -->
    <div class="page-hero">
      <div class="hero-text">
        <h2 class="hero-title">学习资料库</h2>
        <p class="hero-sub">浏览、收藏与点赞优质提示词教程，共 {{ pagination.total }} 篇内容</p>
      </div>
      <div class="hero-stats">
        <div class="stat-pill">
          <el-icon><Reading /></el-icon>
          <span class="num">{{ categoryStats.published || 0 }}</span>
          <span class="lbl">已发布</span>
        </div>
        <div class="stat-pill">
          <el-icon><Star /></el-icon>
          <span class="num">{{ categoryStats.totalLikes || 0 }}</span>
          <span class="lbl">总点赞</span>
        </div>
        <div class="stat-pill">
          <el-icon><View /></el-icon>
          <span class="num">{{ categoryStats.totalViews || 0 }}</span>
          <span class="lbl">总阅读</span>
        </div>
      </div>
    </div>

    <!-- 搜索与筛选 -->
    <el-card class="filter-card" shadow="never">
      <div class="filter-row">
        <el-input
          v-model="searchForm.search"
          placeholder="搜索标题 / 摘要 / 标签"
          clearable
          class="search-input"
          :prefix-icon="Search"
          @input="handleSearchDebounced"
          @keyup.enter="handleSearch"
        />
        <el-select
          v-model="searchForm.category"
          placeholder="全部分类"
          clearable
          class="filter-select"
          @change="handleSearch"
        >
          <el-option label="基础入门" value="basic">
            <span class="opt-dot" style="background:#3B82F6"></span>基础入门
          </el-option>
          <el-option label="进阶技巧" value="intermediate">
            <span class="opt-dot" style="background:#F59E0B"></span>进阶技巧
          </el-option>
          <el-option label="高级应用" value="advanced">
            <span class="opt-dot" style="background:#EF4444"></span>高级应用
          </el-option>
          <el-option label="最佳实践" value="best_practices">
            <span class="opt-dot" style="background:#10B981"></span>最佳实践
          </el-option>
        </el-select>
        <el-select
          v-model="searchForm.status"
          placeholder="全部状态"
          clearable
          class="filter-select"
          @change="handleSearch"
        >
          <el-option label="草稿" value="draft" />
          <el-option label="已发布" value="published" />
          <el-option label="已下架" value="archived" />
        </el-select>
        <el-select
          v-model="searchForm.ordering"
          class="filter-select"
          @change="handleSearch"
        >
          <el-option label="最新发布" value="-created_at" />
          <el-option label="最近更新" value="-updated_at" />
          <el-option label="最热阅读" value="-view_count" />
          <el-option label="最多点赞" value="-like_count" />
        </el-select>
        <el-button @click="handleReset" class="reset-btn">
          <el-icon><Refresh /></el-icon>重置
        </el-button>
      </div>

      <!-- 标签筛选 -->
      <div class="tag-bar">
        <span class="tag-bar-label">
          <el-icon><CollectionTag /></el-icon>标签：
        </span>
        <div class="tag-list">
          <span
            class="filter-tag"
            :class="{ active: !searchForm.tag }"
            @click="selectTag('')"
          >全部</span>
          <span
            v-for="t in popularTags"
            :key="t.name"
            class="filter-tag"
            :class="{ active: searchForm.tag === t.name }"
            @click="selectTag(t.name)"
          >
            #{{ t.name }}
            <span class="tag-count">{{ t.count }}</span>
          </span>
        </div>
      </div>
    </el-card>

    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="left">
        <el-button
          v-if="isAdminOrTeacher"
          type="primary"
          @click="handleCreate"
          round
        >
          <el-icon><Plus /></el-icon>新建内容
        </el-button>
        <el-button
          v-if="isAdmin"
          type="danger"
          :disabled="selectedIds.length === 0"
          @click="handleBatchDelete"
          plain
        >
          <el-icon><Delete /></el-icon>批量删除 ({{ selectedIds.length }})
        </el-button>
      </div>
      <div class="right">
        <el-radio-group v-model="viewMode" size="default">
          <el-radio-button value="card">
            <el-icon><Grid /></el-icon>卡片
          </el-radio-button>
          <el-radio-button value="table">
            <el-icon><List /></el-icon>表格
          </el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <!-- 卡片视图 -->
    <transition name="fade-mode" mode="out-in">
      <div v-if="viewMode === 'card'" key="card" class="card-grid" v-loading="loading">
        <transition-group name="card-list" tag="div" class="card-grid-inner">
          <div
            v-for="item in tableData"
            :key="item.id"
            class="material-card"
            @click="handleView(item)"
          >
            <div class="card-cover" :style="getCoverStyle(item)">
              <div class="cover-overlay">
                <el-tag
                  size="small"
                  :type="getCategoryTagType(item.category)"
                  effect="dark"
                  class="cover-tag"
                >{{ item.category_display || getCategoryLabel(item.category) }}</el-tag>
                <el-tag
                  v-if="item.status !== 'published'"
                  size="small"
                  :type="getStatusTagType(item.status)"
                  effect="dark"
                  class="cover-tag"
                >{{ item.status_display || getStatusLabel(item.status) }}</el-tag>
              </div>
              <div class="cover-icon">
                <el-icon><Document /></el-icon>
              </div>
            </div>

            <div class="card-body">
              <h3 class="card-title">{{ item.title }}</h3>
              <p class="card-summary">{{ item.summary || '暂无摘要' }}</p>

              <div class="card-tags" v-if="item.tags && item.tags.length">
                <span
                  v-for="tag in item.tags.slice(0, 3)"
                  :key="tag"
                  class="card-tag"
                >#{{ tag }}</span>
                <span v-if="item.tags.length > 3" class="card-tag more">+{{ item.tags.length - 3 }}</span>
              </div>
            </div>

            <div class="card-footer">
              <div class="footer-author">
                <el-avatar :size="24" class="footer-avatar">
                  {{ (item.author_name || '匿').charAt(0) }}
                </el-avatar>
                <span class="author-name">{{ item.author_name || '匿名' }}</span>
              </div>
              <div class="footer-meta">
                <span class="meta-item" :title="'阅读 ' + (item.view_count || 0)">
                  <el-icon><View /></el-icon>{{ formatNumber(item.view_count) }}
                </span>
                <span
                  class="meta-item like-btn"
                  :class="{ liked: item.is_liked }"
                  @click.stop="handleLike(item)"
                  :title="item.is_liked ? '取消点赞' : '点赞'"
                >
                  <el-icon><Star /></el-icon>{{ formatNumber(item.like_count) }}
                </span>
              </div>
            </div>
          </div>

          <div v-if="!loading && tableData.length === 0" key="empty" class="empty-card">
            <el-empty description="暂无相关内容，换个关键词试试？" />
          </div>
        </transition-group>
      </div>

      <!-- 表格视图 -->
      <el-card v-else key="table" shadow="never" class="table-card" v-loading="loading">
        <el-table
          ref="tableRef"
          :data="tableData"
          @selection-change="handleSelectionChange"
          :header-cell-style="{ background: '#F9FAFB', color: '#374151', fontWeight: 600 }"
          stripe
        >
          <el-table-column type="selection" width="50" align="center" />

          <el-table-column prop="id" label="ID" width="70" align="center" />

          <el-table-column label="标题信息" min-width="280">
            <template #default="{ row }">
              <div class="title-cell">
                <div class="title-text" @click="handleView(row)">{{ row.title }}</div>
                <div class="title-summary" v-if="row.summary">
                  {{ row.summary.substring(0, 60) }}{{ row.summary.length > 60 ? '...' : '' }}
                </div>
                <div class="title-tags" v-if="row.tags && row.tags.length">
                  <span v-for="t in row.tags.slice(0, 3)" :key="t" class="mini-tag">#{{ t }}</span>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="分类" width="110" align="center">
            <template #default="{ row }">
              <el-tag :type="getCategoryTagType(row.category)" size="small" effect="light">
                {{ row.category_display || getCategoryLabel(row.category) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)" size="small" effect="plain">
                {{ row.status_display || getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="view_count" label="阅读" width="90" align="center">
            <template #default="{ row }">
              <span class="metric">{{ formatNumber(row.view_count) }}</span>
            </template>
          </el-table-column>

          <el-table-column label="点赞" width="100" align="center">
            <template #default="{ row }">
              <span
                class="metric like-cell"
                :class="{ liked: row.is_liked }"
                @click="handleLike(row)"
              >
                <el-icon><Star /></el-icon>{{ formatNumber(row.like_count) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column prop="author_name" label="作者" width="100" align="center" show-overflow-tooltip />

          <el-table-column prop="created_at" label="创建时间" width="170">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>

          <el-table-column label="操作" width="220" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="handleView(row)">
                <el-icon><View /></el-icon>查看
              </el-button>
              <el-button
                v-if="isAdminOrTeacher && (isAdmin || row.author === currentUser?.id)"
                type="warning"
                link
                size="small"
                @click="handleEdit(row)"
              >
                <el-icon><Edit /></el-icon>编辑
              </el-button>
              <el-button
                v-if="isAdmin"
                type="danger"
                link
                size="small"
                @click="handleDelete(row)"
              >
                <el-icon><Delete /></el-icon>删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </transition>

    <!-- 分页 -->
    <div class="pagination-wrapper" v-if="pagination.total > 0">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[12, 24, 48]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  Plus,
  Delete,
  Reading,
  Star,
  View,
  Edit,
  Document,
  Grid,
  List,
  CollectionTag
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/modules/auth'
import {
  getMaterialList,
  deleteMaterial,
  batchDeleteMaterials,
  toggleLike,
  getStatistics
} from '@/api/learning'

const router = useRouter()
const authStore = useAuthStore()

const isAdmin = computed(() => authStore.isAdmin)
const isAdminOrTeacher = computed(() => authStore.isAdminOrTeacher)
const currentUser = computed(() => authStore.user)

const tableRef = ref(null)
const loading = ref(false)
const tableData = ref([])
const selectedIds = ref([])
const viewMode = ref(localStorage.getItem('learning_list_view') || 'card')

const searchForm = reactive({
  search: '',
  category: '',
  status: '',
  tag: '',
  ordering: '-created_at'
})

const pagination = reactive({
  page: 1,
  pageSize: 12,
  total: 0
})

const categoryStats = ref({})
const popularTags = ref([])

let searchTimer = null
function handleSearchDebounced() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    pagination.page = 1
    fetchMaterialList()
  }, 350)
}

watch(viewMode, (v) => localStorage.setItem('learning_list_view', v))

onMounted(() => {
  fetchMaterialList()
  fetchStats()
})

async function fetchMaterialList() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm
    }
    Object.keys(params).forEach(k => { if (!params[k]) delete params[k] })

    const res = await getMaterialList(params)
    const data = res.data.data || res.data
    tableData.value = data.results || data
    pagination.total = data.count || 0

    // 收集标签
    collectPopularTags()
  } catch (error) {
    console.error('获取学习资料失败:', error)
  } finally {
    loading.value = false
  }
}

function collectPopularTags() {
  const map = new Map()
  tableData.value.forEach(item => {
    (item.tags || []).forEach(tag => {
      map.set(tag, (map.get(tag) || 0) + 1)
    })
  })
  popularTags.value = Array.from(map.entries())
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 12)
}

async function fetchStats() {
  try {
    const res = await getStatistics()
    const data = res.data.data || res.data
    categoryStats.value = {
      published: data.overview?.published || 0,
      totalLikes: (data.popular_materials || []).reduce((s, m) => s + (m.like_count || 0), 0),
      totalViews: data.overview?.total_views || 0
    }
  } catch (e) {
    /* ignore */
  }
}

function selectTag(tag) {
  searchForm.tag = tag
  handleSearch()
}

function handleSearch() {
  pagination.page = 1
  fetchMaterialList()
}

function handleReset() {
  Object.assign(searchForm, {
    search: '',
    category: '',
    status: '',
    tag: '',
    ordering: '-created_at'
  })
  handleSearch()
}

function handleSelectionChange(selection) {
  selectedIds.value = selection.map(i => i.id)
}

function handleSizeChange(size) {
  pagination.pageSize = size
  pagination.page = 1
  fetchMaterialList()
}

function handlePageChange(page) {
  pagination.page = page
  fetchMaterialList()
}

function handleCreate() {
  router.push('/learning/create')
}

function handleView(row) {
  router.push(`/learning/detail/${row.id}`)
}

function handleEdit(row) {
  router.push(`/learning/edit/${row.id}`)
}

async function handleLike(row) {
  if (!currentUser.value) {
    ElMessage.warning('请先登录')
    return
  }
  try {
    const res = await toggleLike(row.id)
    const result = res.data.data || res.data
    row.is_liked = result.liked
    row.like_count = result.like_count
    ElMessage.success(result.liked ? '已点赞 ⭐' : '已取消点赞')
  } catch (e) {
    console.error(e)
    ElMessage.error('操作失败')
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
    ElMessage.success('删除成功')
    fetchMaterialList()
  } catch (error) {
    if (error !== 'cancel') console.error('删除失败:', error)
  }
}

async function handleBatchDelete() {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 个学习资料吗？`,
      '批量删除警告',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    await batchDeleteMaterials(selectedIds.value)
    ElMessage.success(`成功删除 ${selectedIds.value.length} 个`)
    selectedIds.value = []
    fetchMaterialList()
  } catch (error) {
    if (error !== 'cancel') console.error('批量删除失败:', error)
  }
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
function getCoverStyle(item) {
  const colors = {
    basic: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)',
    intermediate: 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
    advanced: 'linear-gradient(135deg, #EF4444 0%, #B91C1C 100%)',
    best_practices: 'linear-gradient(135deg, #10B981 0%, #047857 100%)'
  }
  return { background: colors[item.category] || colors.basic }
}
function formatNumber(n) {
  if (!n) return '0'
  if (n >= 10000) return (n / 10000).toFixed(1) + 'w'
  return n.toString()
}
function formatDate(s) {
  if (!s) return '-'
  return new Date(s).toLocaleString('zh-CN', { hour12: false })
}
</script>

<style scoped>
.learning-list-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 顶部 Hero */
.page-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 50%, #3B82F6 100%);
  border-radius: 16px;
  color: #ffffff;
  position: relative;
  overflow: hidden;
}

.page-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 90% -20%, rgba(255,255,255,0.18), transparent 50%);
  pointer-events: none;
}

.hero-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 4px;
}

.hero-sub {
  margin: 0;
  font-size: 14px;
  opacity: 0.85;
}

.hero-stats {
  display: flex;
  gap: 12px;
}

.stat-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 999px;
  backdrop-filter: blur(8px);
  font-size: 13px;
}

.stat-pill .num {
  font-size: 18px;
  font-weight: 700;
}

.stat-pill .lbl {
  opacity: 0.85;
}

/* 筛选卡 */
.filter-card :deep(.el-card__body) {
  padding: 16px 20px;
}

.filter-row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 240px;
  max-width: 360px;
}

.filter-select {
  width: 150px;
}

.reset-btn {
  margin-left: auto;
}

.tag-bar {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px dashed #E5E7EB;
}

.tag-bar-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #6B7280;
  font-weight: 500;
  flex-shrink: 0;
  padding-top: 4px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.filter-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: #F3F4F6;
  color: #4B5563;
  border-radius: 999px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.filter-tag:hover {
  background: #E5E7EB;
  color: #111827;
}

.filter-tag.active {
  background: #2563EB;
  color: #ffffff;
}

.filter-tag .tag-count {
  font-size: 10px;
  opacity: 0.8;
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 4px;
}

.toolbar .left {
  display: flex;
  gap: 10px;
}

/* 卡片视图 */
.card-grid {
  min-height: 200px;
}

.card-grid-inner {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.material-card {
  background: #ffffff;
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  border: 1px solid #F3F4F6;
  display: flex;
  flex-direction: column;
}

.material-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.1);
  border-color: transparent;
}

.card-cover {
  height: 130px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.85);
}

.cover-icon {
  font-size: 48px;
  opacity: 0.7;
}

.cover-overlay {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  gap: 6px;
}

.cover-tag {
  font-weight: 500;
}

.card-body {
  padding: 16px 18px 8px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-summary {
  font-size: 13px;
  color: #6B7280;
  margin: 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: auto;
  padding-top: 4px;
}

.card-tag {
  font-size: 11px;
  color: #6B7280;
  background: #F3F4F6;
  padding: 2px 6px;
  border-radius: 4px;
}

.card-tag.more {
  background: transparent;
  color: #9CA3AF;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 18px;
  border-top: 1px solid #F3F4F6;
  background: #FAFAFA;
}

.footer-author {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

.footer-avatar {
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  color: #ffffff;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.author-name {
  font-size: 12px;
  color: #4B5563;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.footer-meta {
  display: flex;
  gap: 12px;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  color: #6B7280;
}

.meta-item .el-icon {
  font-size: 14px;
}

.like-btn {
  cursor: pointer;
  transition: color 0.2s;
  user-select: none;
}

.like-btn:hover {
  color: #F59E0B;
}

.like-btn.liked {
  color: #F59E0B;
  font-weight: 600;
}

.empty-card {
  grid-column: 1 / -1;
  padding: 60px 20px;
  text-align: center;
}

/* 表格视图 */
.table-card :deep(.el-card__body) {
  padding: 0;
}

.title-cell {
  line-height: 1.5;
}

.title-text {
  font-weight: 500;
  color: #111827;
  cursor: pointer;
  margin-bottom: 4px;
}

.title-text:hover {
  color: #2563EB;
}

.title-summary {
  font-size: 12px;
  color: #6B7280;
  margin-bottom: 4px;
}

.title-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.mini-tag {
  font-size: 10px;
  color: #6B7280;
  background: #F3F4F6;
  padding: 1px 5px;
  border-radius: 4px;
}

.metric {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 13px;
  color: #6B7280;
}

.metric .el-icon {
  font-size: 13px;
}

.like-cell {
  cursor: pointer;
  transition: color 0.2s;
  user-select: none;
}

.like-cell:hover {
  color: #F59E0B;
}

.like-cell.liked {
  color: #F59E0B;
  font-weight: 600;
}

.opt-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
  vertical-align: middle;
}

/* 分页 */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 8px 0 24px;
}

/* 视图切换动画 */
.fade-mode-enter-active,
.fade-mode-leave-active {
  transition: opacity 0.25s;
}

.fade-mode-enter-from,
.fade-mode-leave-to {
  opacity: 0;
}

.card-list-enter-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.card-list-enter-from {
  opacity: 0;
  transform: translateY(10px) scale(0.98);
}

/* 响应式 */
@media (max-width: 768px) {
  .page-hero {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding: 20px;
  }
  .hero-stats {
    flex-wrap: wrap;
  }
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }
  .search-input,
  .filter-select {
    width: 100%;
    max-width: none;
  }
  .reset-btn {
    margin-left: 0;
  }
  .card-grid-inner {
    grid-template-columns: 1fr;
  }
}
</style>
