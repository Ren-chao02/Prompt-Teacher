<template>
  <div class="learning-list-container">
    <!-- 搜索和筛选栏 -->
    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.search"
            placeholder="标题/摘要/标签"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item label="分类">
          <el-select
            v-model="searchForm.category"
            placeholder="全部分类"
            clearable
            style="width: 140px"
          >
            <el-option label="基础入门" value="basic" />
            <el-option label="进阶技巧" value="intermediate" />
            <el-option label="高级应用" value="advanced" />
            <el-option label="最佳实践" value="best_practices" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select
            v-model="searchForm.status"
            placeholder="全部状态"
            clearable
            style="width: 120px"
          >
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
            <el-option label="已下架" value="archived" />
          </el-select>
        </el-form-item>

        <el-form-item label="排序">
          <el-select
            v-model="searchForm.ordering"
            placeholder="默认排序"
            style="width: 150px"
            @change="handleSearch"
          >
            <el-option label="创建时间 ↓" value="-created_at" />
            <el-option label="创建时间 ↑" value="created_at" />
            <el-option label="更新时间 ↓" value="-updated_at" />
            <el-option label="阅读量 ↓" value="-view_count" />
            <el-option label="阅读量 ↑" value="view_count" />
            <el-option label="排序权重 ↓" value="-order_index" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon> 重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="left">
        <el-button 
          type="primary" 
          @click="handleCreate" 
          v-if="isAdminOrTeacher"
        >
          <el-icon><Plus /></el-icon> 新建内容
        </el-button>
        <el-button 
          type="danger" 
          :disabled="selectedIds.length === 0"
          @click="handleBatchDelete"
          v-if="isAdmin"
        >
          <el-icon><Delete /></el-icon> 批量删除 ({{ selectedIds.length }})
        </el-button>
      </div>
      <div class="right">
        <span class="total-info">共 {{ pagination.total }} 条记录</span>
      </div>
    </div>

    <!-- 数据表格 -->
    <el-card shadow="never">
      <el-table
        ref="tableRef"
        :data="tableData"
        v-loading="loading"
        border
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" align="center" />

        <el-table-column prop="id" label="ID" width="70" align="center" />

        <el-table-column label="标题信息" min-width="250">
          <template #default="{ row }">
            <div class="title-cell">
              <div class="title">{{ row.title }}</div>
              <div class="summary" v-if="row.summary">
                {{ row.summary.substring(0, 80) }}{{ row.summary.length > 80 ? '...' : '' }}
              </div>
              <div class="tags" v-if="row.tags && row.tags.length">
                <el-tag
                  v-for="tag in row.tags.slice(0, 3)"
                  :key="tag"
                  size="small"
                  type="info"
                  style="margin-right: 4px; margin-top: 4px;"
                >
                  {{ tag }}
                </el-tag>
                <el-tag 
                  v-if="row.tags.length > 3" 
                  size="small" 
                  type="info"
                >
                  +{{ row.tags.length - 3 }}
                </el-tag>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="category" label="分类" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">
              {{ getCategoryLabel(row.category) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="view_count" label="阅读量" width="90" align="center" sortable>
          <template #default="{ row }">
            <span class="view-count">👁️ {{ formatNumber(row.view_count) }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="order_index" label="排序" width="80" align="center" sortable />

        <el-table-column prop="author_name" label="作者" width="100" align="center" show-overflow-tooltip />

        <el-table-column prop="created_at" label="创建时间" width="170" sortable>
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="240" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button 
              type="warning" 
              link 
              size="small" 
              @click="handleEdit(row)"
              v-if="isAdminOrTeacher && (isAdmin || row.author === currentUser.id)"
            >
              编辑
            </el-button>
            <el-button 
              :type="row.status === 'published' ? 'info' : 'success'"
              link 
              size="small" 
              @click="handleToggleStatus(row)"
              v-if="isAdminOrTeacher && (isAdmin || row.author === currentUser.id)"
            >
              {{ row.status === 'published' ? '下架' : '发布' }}
            </el-button>
            <el-button 
              type="danger" 
              link 
              size="small" 
              @click="handleDelete(row)"
              v-if="isAdmin"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Delete } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/modules/auth'
import {
  getMaterialList,
  deleteMaterial,
  batchDeleteMaterials,
  publishMaterial,
  archiveMaterial
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

const searchForm = reactive({
  search: '',
  category: '',
  status: '',
  ordering: '-created_at'
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

onMounted(() => {
  fetchMaterialList()
})

async function fetchMaterialList() {
  loading.value = true
  
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm
    }
    
    const res = await getMaterialList(params)
    tableData.value = res.data.results || res.data
    pagination.total = res.data.count || (res.data.results ? res.data.count : res.data.length)
  } catch (error) {
    console.error('获取学习资料列表失败:', error)
  } finally {
    loading.value = false
  }
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
    ordering: '-created_at'
  })
  handleSearch()
}

function handleSelectionChange(selection) {
  selectedIds.value = selection.map(item => item.id)
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

async function handleToggleStatus(row) {
  const action = row.status === 'published' ? 'archive' : 'publish'
  const actionText = row.status === 'published' ? '下架' : '发布'
  
  try {
    await ElMessageBox.confirm(
      `确定要${actionText}《${row.title}》吗？`,
      '确认操作',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    
    if (action === 'publish') {
      await publishMaterial(row.id)
      ElMessage.success(`《${row.title}》已发布`)
    } else {
      await archiveMaterial(row.id)
      ElMessage.success(`《${row.title}》已下架`)
    }
    
    fetchMaterialList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
    }
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
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
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
    ElMessage.success(`成功删除 ${selectedIds.value.length} 个学习资料`)
    selectedIds.value = []
    fetchMaterialList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
    }
  }
}

function getCategoryType(category) {
  const map = {
    basic: '',
    intermediate: 'warning',
    advanced: 'danger',
    best_practices: 'success'
  }
  return map[category] || 'info'
}

function getCategoryLabel(category) {
  const map = {
    basic: '基础入门',
    intermediate: '进阶技巧',
    advanced: '高级应用',
    best_practices: '最佳实践'
  }
  return map[category] || category
}

function getCategoryTagType(category) {
  const map = {
    basic: '',
    intermediate: 'warning',
    advanced: 'danger',
    best_practices: 'success'
  }
  return map[category] || 'info'
}

function getStatusTagType(status) {
  const map = {
    draft: 'info',
    published: 'success',
    archived: 'danger'
  }
  return map[status] || 'info'
}

function getStatusLabel(status) {
  const map = {
    draft: '草稿',
    published: '已发布',
    archived: '已下架'
  }
  return map[status] || status
}

function formatNumber(num) {
  if (!num) return '0'
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  }
  return num.toString()
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.learning-list-container {
  padding: 0;
}

.search-card {
  margin-bottom: 16px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 0 4px;
}

.toolbar .left,
.toolbar .right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.total-info {
  color: #909399;
  font-size: 14px;
}

.title-cell {
  line-height: 1.5;
}

.title-cell .title {
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  cursor: pointer;
}

.title-cell .title:hover {
  color: #409EFF;
}

.title-cell .summary {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
  line-height: 1.4;
}

.title-cell .tags {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
}

.view-count {
  font-size: 13px;
  color: #606266;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}
</style>
