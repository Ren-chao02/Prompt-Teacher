<template>
  <div class="user-list-container">
    <!-- 搜索和筛选栏 -->
    <el-card class="search-card" shadow="never">
      <el-form :model="searchForm" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.search"
            placeholder="用户名/邮箱/学号"
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item label="角色">
          <el-select
            v-model="searchForm.role"
            placeholder="全部角色"
            clearable
            style="width: 120px"
          >
            <el-option label="管理员" value="admin" />
            <el-option label="教师" value="teacher" />
            <el-option label="学生" value="student" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select
            v-model="searchForm.is_active"
            placeholder="全部状态"
            clearable
            style="width: 100px"
          >
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>

        <el-form-item label="班级">
          <el-select v-model="searchForm.class_info" placeholder="全部班级" clearable style="width: 160px">
            <el-option v-for="c in classList" :key="c.id" :label="c.name" :value="c.id" />
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
        <el-button type="primary" @click="handleCreate" v-if="isAdmin">
          <el-icon><Plus /></el-icon> 新建用户
        </el-button>
        <el-button type="success" @click="importVisible = true" v-if="isAdmin">
          <el-icon><Upload /></el-icon> 批量导入
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

        <el-table-column label="用户信息" min-width="200">
          <template #default="{ row }">
            <div class="user-info-cell">
              <el-avatar :size="40" :src="row.avatar || undefined">
                {{ (row.real_name || row.username)?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <div class="info">
                <div class="username">{{ row.real_name || row.username }}</div>
                <div class="email">{{ row.email }}</div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="role" label="角色" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getRoleTagType(row.role)" size="small">
              {{ getRoleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="标识符" width="130" align="center">
          <template #default="{ row }">
            <span v-if="row.student_id">{{ row.student_id }}</span>
            <span v-else-if="row.employee_id">{{ row.employee_id }}</span>
            <span v-else style="color:#999">-</span>
          </template>
        </el-table-column>

        <el-table-column prop="class_name" label="班级" width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ row.class_name || '-' }}</template>
        </el-table-column>

        <el-table-column prop="is_active" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              :disabled="!isAdmin || row.id === currentUser.id"
              @change="(val) => handleStatusChange(row, val)"
            />
          </template>
        </el-table-column>

        <el-table-column prop="date_joined" label="注册时间" width="170" sortable>
          <template #default="{ row }">
            {{ formatDate(row.date_joined) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button 
              type="warning" 
              link 
              size="small" 
              @click="handleResetPassword(row)"
              v-if="isAdmin && row.id !== currentUser.id"
            >
              重置密码
            </el-button>
            <el-button 
              type="danger" 
              link 
              size="small" 
              @click="handleDelete(row)"
              v-if="isAdmin && row.id !== currentUser.id"
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
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <UserDialog
      v-model:visible="dialogVisible"
      :user-data="currentUserData"
      :is-edit="isEditMode"
      @success="handleDialogSuccess"
    />

    <!-- 重置密码对话框 -->
    <ResetPasswordDialog
      v-model:visible="resetPasswordVisible"
      :user="resetPasswordUser"
      @success="handleResetPasswordSuccess"
    />

    <!-- 批量导入对话框 -->
    <BatchImportDialog
      v-model:visible="importVisible"
      @success="fetchUserList"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus, Delete, Upload } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/modules/auth'
import { getUserList, deleteUser, batchDeleteUsers, changeUserStatus, getClassList } from '@/api/user'
import UserDialog from './components/UserDialog.vue'
import ResetPasswordDialog from './components/ResetPasswordDialog.vue'
import BatchImportDialog from './components/BatchImportDialog.vue'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.isAdmin)
const currentUser = computed(() => authStore.user)

const tableRef = ref(null)
const loading = ref(false)
const tableData = ref([])
const selectedIds = ref([])

const searchForm = reactive({
  search: '',
  role: '',
  is_active: '',
  class_info: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const importVisible = ref(false)
const classList = ref([])

const dialogVisible = ref(false)
const isEditMode = ref(false)
const currentUserData = ref(null)

const resetPasswordVisible = ref(false)
const resetPasswordUser = ref(null)

onMounted(() => {
  fetchUserList()
  loadClassList()
})

async function loadClassList() {
  try {
    const res = await getClassList({ page_size: 200 })
    // 兼容分页格式 {count, results} 和包装格式 {data: {results}}
    const payload = res.data || res
    classList.value = payload.results || (Array.isArray(payload) ? payload : [])
  } catch (e) { console.error(e) }
}

async function fetchUserList() {
  loading.value = true
  
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ordering: '-date_joined',
      ...searchForm
    }
    
    const res = await getUserList(params)
    // DRF 分页格式: { count, results, next, previous }
    // 非分页/空结果: [] 或 { count: 0, results: [] }
    const payload = res.data
    if (payload && typeof payload === 'object' && 'results' in payload) {
      tableData.value = payload.results || []
      pagination.total = payload.count || 0
    } else {
      tableData.value = Array.isArray(payload) ? payload : []
      pagination.total = tableData.value.length
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchUserList()
}

function handleReset() {
  Object.assign(searchForm, {
    search: '',
    role: '',
    is_active: '',
    class_info: ''
  })
  handleSearch()
}

function handleSelectionChange(selection) {
  selectedIds.value = selection.map(item => item.id)
}

function handleSizeChange(size) {
  pagination.pageSize = size
  pagination.page = 1
  fetchUserList()
}

function handlePageChange(page) {
  pagination.page = page
  fetchUserList()
}

function handleCreate() {
  isEditMode.value = false
  currentUserData.value = null
  dialogVisible.value = true
}

function handleEdit(row) {
  isEditMode.value = true
  currentUserData.value = { ...row }
  dialogVisible.value = true
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${row.username}" 吗？此操作不可恢复！`,
      '警告',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    
    await deleteUser(row.id)
    ElMessage.success('删除成功')
    fetchUserList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

async function handleBatchDelete() {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedIds.value.length} 个用户吗？此操作不可恢复！`,
      '批量删除警告',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    
    await batchDeleteUsers(selectedIds.value)
    ElMessage.success(`成功删除 ${selectedIds.value.length} 个用户`)
    selectedIds.value = []
    fetchUserList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
    }
  }
}

async function handleStatusChange(row, isActive) {
  try {
    await changeUserStatus(row.id, isActive)
    ElMessage.success(`已${isActive ? '启用' : '禁用'}用户 ${row.username}`)
  } catch (error) {
    row.is_active = !isActive
    ElMessage.error('状态修改失败')
  }
}

function handleResetPassword(row) {
  resetPasswordUser.value = row
  resetPasswordVisible.value = true
}

function handleDialogSuccess() {
  dialogVisible.value = false
  fetchUserList()
}

function handleResetPasswordSuccess() {
  resetPasswordVisible.value = false
}

function getRoleType(role) {
  const map = { admin: 'danger', teacher: 'warning', student: '' }
  return map[role] || 'info'
}

function getRoleLabel(role) {
  const map = { admin: '管理员', teacher: '教师', student: '学生' }
  return map[role] || role
}

function getRoleTagType(role) {
  const map = { admin: 'danger', teacher: 'warning', student: '' }
  return map[role] || 'info'
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
.user-list-container {
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

.user-info-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info-cell .info {
  flex: 1;
}

.user-info-cell .username {
  font-weight: 500;
  color: #303133;
  margin-bottom: 2px;
}

.user-info-cell .email {
  font-size: 13px;
  color: #909399;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}
</style>
