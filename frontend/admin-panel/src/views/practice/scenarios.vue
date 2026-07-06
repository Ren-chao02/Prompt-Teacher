<template>
  <div class="scenario-management">
    <div class="page-header">
      <h2>练习场景管理</h2>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建场景
      </el-button>
    </div>

    <div class="filter-bar">
      <el-row :gutter="16" align="middle">
        <el-col :span="6">
          <el-input
            v-model="filters.keyword"
            placeholder="搜索场景标题/ID"
            clearable
            @clear="loadData"
            @keyup.enter="loadData"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.status" placeholder="状态筛选" clearable @change="loadData">
            <el-option label="已发布" value="published" />
            <el-option label="草稿" value="draft" />
            <el-option label="已下架" value="archived" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select v-model="filters.difficulty" placeholder="难度筛选" clearable @change="loadData">
            <el-option label="初级" value="beginner" />
            <el-option label="中级" value="intermediate" />
            <el-option label="高级" value="advanced" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filters.ordering" placeholder="排序方式" clearable @change="loadData">
            <el-option label="创建时间 ↓" value="-created_at" />
            <el-option label="创建时间 ↑" value="created_at" />
            <el-option label="排序权重 ↓" value="-order" />
            <el-option label="查看次数 ↓" value="-view_count" />
            <el-option label="练习次数 ↓" value="-practice_count" />
          </el-select>
        </el-col>
        <el-col :span="4" class="text-right">
          <el-button-group>
            <el-button :type="viewMode === 'grid' ? 'primary' : ''" @click="viewMode = 'grid'">
              <el-icon><Grid /></el-icon>
            </el-button>
            <el-button :type="viewMode === 'table' ? 'primary' : ''" @click="viewMode = 'table'">
              <el-icon><List /></el-icon>
            </el-button>
          </el-button-group>
        </el-col>
      </el-row>
    </div>

    <div v-if="loading && scenarios.length === 0" class="loading-container">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else-if="viewMode === 'grid'" class="scenarios-grid">
      <el-row :gutter="20">
        <el-col
          v-for="item in scenarios"
          :key="item.id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
        >
          <el-card
            class="scenario-card"
            shadow="hover"
            @click="handleView(item)"
          >
            <div class="card-header">
              <div class="icon-wrapper">{{ item.icon || '🎯' }}</div>
              <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, item)">
                <el-button text type="info" @click.stop>
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="edit">编辑</el-dropdown-item>
                    <el-dropdown-item command="topics">管理主题</el-dropdown-item>
                    <el-dropdown-item :command="item.status === 'published' ? 'archive' : 'publish'">
                      {{ item.status === 'published' ? '下架' : '发布' }}
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>

            <div class="card-body">
              <h3 class="title">{{ item.title }}</h3>
              <p class="description">{{ item.description?.substring(0, 80) }}{{ item.description?.length > 80 ? '...' : '' }}</p>

              <div class="meta-tags">
                <el-tag :type="getDifficultyType(item.difficulty)" size="small">
                  {{ getDifficultyLabel(item.difficulty) }}
                </el-tag>
                <el-tag :type="getStatusType(item.status)" size="small">
                  {{ getStatusLabel(item.status) }}
                </el-tag>
                <el-tag size="small" class="topic-count">
                  主题: {{ item.topics_count || 0 }}
                </el-tag>
              </div>

              <div class="stats-row">
                <div class="stat-item">
                  <el-icon><View /></el-icon>
                  <span>{{ formatNumber(item.view_count) }}</span>
                </div>
                <div class="stat-item">
                  <el-icon><TrendCharts /></el-icon>
                  <span>{{ formatNumber(item.practice_count) }}</span>
                </div>
                <div class="stat-item">
                  <el-icon><Star /></el-icon>
                  <span>{{ item.avg_score?.toFixed(1) || '0.0' }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div v-else class="scenarios-table">
      <el-table :data="scenarios" stripe @row-click="handleView">
        <el-table-column prop="icon" label="图标" width="80" align="center">
          <template #default="{ row }">
            <span style="font-size: 24px;">{{ row.icon || '🎯' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="difficulty" label="难度" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getDifficultyType(row.difficulty)" size="small">
              {{ getDifficultyLabel(row.difficulty) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="主题数" width="90" align="center">
          <template #default="{ row }">
            <el-badge :value="row.topics_count || 0" type="primary" />
          </template>
        </el-table-column>
        
        <el-table-column label="统计" width="200" align="center">
          <template #default="{ row }">
            <span class="stats-inline">
              👁️ {{ formatNumber(row.view_count) }} | 
              📊 {{ formatNumber(row.practice_count) }} | 
              ⭐ {{ row.avg_score?.toFixed(1) || '0.0' }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180" sortable>
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click.stop="handleEdit(row)">编辑</el-button>
            <el-button text type="warning" size="small" @click.stop="handleManageTopics(row)">主题</el-button>
            <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, row)">
              <el-button text size="small" @click.stop>更多</el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="row.status === 'published' ? 'archive' : 'publish'">
                    {{ row.status === 'published' ? '下架' : '发布' }}
                  </el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div v-if="total > pageSize" class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[12, 24, 48]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
        label-position="top"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="场景ID" prop="scenario_id">
              <el-input v-model="formData.scenario_id" placeholder="例如: coding_quality" :disabled="!!editingId" />
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="图标" prop="icon">
              <el-input v-model="formData.icon" placeholder="选择图标 emoji 或文字">
                <template #append>
                  <el-popover placement="bottom" :width="300" trigger="click">
                    <template #reference>
                      <el-button>选择</el-button>
                    </template>
                    <div class="emoji-picker">
                      <span
                        v-for="emoji in emojis"
                        :key="emoji"
                        class="emoji-item"
                        @click="formData.icon = emoji"
                      >{{ emoji }}</span>
                    </div>
                  </el-popover>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="场景标题" prop="title">
          <el-input v-model="formData.title" placeholder="输入场景标题" maxlength="100" show-word-limit />
        </el-form-item>

        <el-form-item label="场景描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="描述这个练习场景的目标和内容..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="难度等级" prop="difficulty">
              <el-select v-model="formData.difficulty" placeholder="选择难度">
                <el-option label="初级 (Beginner)" value="beginner" />
                <el-option label="中级 (Intermediate)" value="intermediate" />
                <el-option label="高级 (Advanced)" value="advanced" />
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="8">
            <el-form-item label="排序权重" prop="order">
              <el-input-number v-model="formData.order" :min="0" :max="9999" />
            </el-form-item>
          </el-col>
          
          <el-col :span="8">
            <el-form-item label="初始状态" prop="status">
              <el-select v-model="formData.status" placeholder="选择状态">
                <el-option label="草稿" value="draft" />
                <el-option label="直接发布" value="published" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="封面图片 URL (可选)">
          <el-input v-model="formData.cover_image" placeholder="https://example.com/image.jpg" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ editingId ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      :title="'场景详情 - ' + currentScenario?.title"
      size="600px"
      direction="rtl"
    >
      <template v-if="currentScenario">
        <div class="detail-content">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="图标">
              <span style="font-size: 32px;">{{ currentScenario.icon }}</span>
            </el-descriptions-item>
            
            <el-descriptions-item label="场景ID">
              <el-tag>{{ currentScenario.scenario_id }}</el-tag>
            </el-descriptions-item>
            
            <el-descriptions-item label="标题">
              {{ currentScenario.title }}
            </el-descriptions-item>
            
            <el-descriptions-item label="描述">
              {{ currentScenario.description }}
            </el-descriptions-item>
            
            <el-descriptions-item label="难度">
              <el-tag :type="getDifficultyType(currentScenario.difficulty)">
                {{ getDifficultyLabel(currentScenario.difficulty) }}
              </el-tag>
            </el-descriptions-item>
            
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(currentScenario.status)">
                {{ getStatusLabel(currentScenario.status) }}
              </el-tag>
            </el-descriptions-item>
            
            <el-descriptions-item label="统计信息">
              <div class="detail-stats">
                <div class="stat-box">
                  <div class="value">{{ formatNumber(currentScenario.view_count) }}</div>
                  <div class="label">查看次数</div>
                </div>
                <div class="stat-box">
                  <div class="value">{{ formatNumber(currentScenario.practice_count) }}</div>
                  <div class="label">练习次数</div>
                </div>
                <div class="stat-box">
                  <div class="value">{{ currentScenario.avg_score?.toFixed(1) || '0.0' }}</div>
                  <div class="label">平均分</div>
                </div>
              </div>
            </el-descriptions-item>
            
            <el-descriptions-item label="主题列表">
              <div v-if="currentScenario.topics?.length" class="topics-list">
                <el-tag
                  v-for="topic in currentScenario.topics"
                  :key="topic.id"
                  class="topic-tag"
                  effect="plain"
                >
                  主题{{ topic.topic_number }}: {{ topic.title }}
                </el-tag>
              </div>
              <el-empty v-else description="暂无主题" :image-size="60" />
            </el-descriptions-item>
            
            <el-descriptions-item label="创建者">
              {{ currentScenario.author_name || '系统' }}
            </el-descriptions-item>
            
            <el-descriptions-item label="时间信息">
              创建: {{ formatDate(currentScenario.created_at) }}<br/>
              更新: {{ formatDate(currentScenario.updated_at) }}
            </el-descriptions-item>
          </el-descriptions>

          <div class="drawer-actions">
            <el-button type="primary" @click="handleEditFromDrawer">编辑场景</el-button>
            <el-button type="success" @click="handleManageTopics(currentScenario)">管理主题</el-button>
            <el-button
              :type="currentScenario.status === 'published' ? 'warning' : 'success'"
              @click="handleTogglePublish(currentScenario)"
            >
              {{ currentScenario.status === 'published' ? '下架' : '发布' }}
            </el-button>
          </div>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Grid, List, MoreFilled,
  View, TrendCharts, Star
} from '@element-plus/icons-vue'
import {
  getScenarioList, createScenario, updateScenario, deleteScenario, publishScenario
} from '@/api/practice'

const router = useRouter()

const loading = ref(false)
const viewMode = ref('grid')
const scenarios = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)

const filters = reactive({
  keyword: '',
  status: '',
  difficulty: '',
  ordering: '-created_at'
})

const dialogVisible = ref(false)
const drawerVisible = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const formRef = ref(null)
const currentScenario = ref(null)

const formData = reactive({
  scenario_id: '',
  title: '',
  description: '',
  icon: '🎯',
  difficulty: 'intermediate',
  order: 0,
  status: 'draft',
  cover_image: ''
})

const formRules = {
  scenario_id: [
    { required: true, message: '请输入场景ID', trigger: 'blur' },
    { pattern: /^[a-z_]+$/, message: '只能包含小写字母和下划线', trigger: 'blur' }
  ],
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在2到100个字符之间', trigger: 'blur' }
  ],
  difficulty: [
    { required: true, message: '请选择难度', trigger: 'change' }
  ]
}

const emojis = ['🎯', '💻', '📝', '📊', '🎨', '🔬', '🚀', '💡', '📚', '🔧', '⭐', '🌟', '🎮', '🏆', '📈', '🔥']

onMounted(() => {
  loadData()
})

async function loadData() {
  loading.value = true
  
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ordering: filters.ordering
    }
    
    if (filters.keyword) params.search = filters.keyword
    if (filters.status) params.status = filters.status
    if (filters.difficulty) params.difficulty = filters.difficulty
    
    const res = await getScenarioList(params)
    
    if (res.code === 200) {
      scenarios.value = res.data.results || res.data
      total.value = res.data.count || scenarios.value.length
    }
  } catch (error) {
    console.error('加载场景数据失败:', error)
  } finally {
    loading.value = false
  }
}

function getDialogTitle() {
  return editingId.value ? '编辑场景' : '新建场景'
}

function resetForm() {
  Object.assign(formData, {
    scenario_id: '',
    title: '',
    description: '',
    icon: '🎯',
    difficulty: 'intermediate',
    order: 0,
    status: 'draft',
    cover_image: ''
  })
  editingId.value = null
}

function handleCreate() {
  resetForm()
  dialogVisible.value = true
}

function handleEdit(item) {
  editingId.value = item.id
  Object.assign(formData, {
    scenario_id: item.scenario_id,
    title: item.title,
    description: item.description,
    icon: item.icon || '🎯',
    difficulty: item.difficulty,
    order: item.order,
    status: item.status,
    cover_image: item.cover_image || ''
  })
  dialogVisible.value = true
}

function handleEditFromDrawer() {
  drawerVisible.value = false
  handleEdit(currentScenario.value)
}

function handleView(item) {
  currentScenario.value = item
  drawerVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  
  submitting.value = true
  
  try {
    let res
    if (editingId.value) {
      res = await updateScenario(editingId.value, formData)
      ElMessage.success('场景更新成功')
    } else {
      res = await createScenario(formData)
      ElMessage.success('场景创建成功')
    }
    
    dialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    submitting.value = false
  }
}

async function handleDelete(item) {
  try {
    await ElMessageBox.confirm(
      `确定要删除场景 "${item.title}" 吗？此操作不可恢复！`,
      '确认删除',
      { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
    )
    
    await deleteScenario(item.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

async function handleTogglePublish(item) {
  const action = item.status === 'published' ? 'archive' : 'publish'
  
  try {
    await publishScenario(item.id, action)
    ElMessage.success(action === 'publish' ? '发布成功' : '下架成功')
    
    if (drawerVisible.value) {
      currentScenario.value.status = action === 'publish' ? 'published' : 'archived'
    }
    
    loadData()
  } catch (error) {
    console.error('操作失败:', error)
  }
}

async function handleCommand(command, item) {
  switch (command) {
    case 'edit':
      handleEdit(item)
      break
    case 'topics':
      handleManageTopics(item)
      break
    case 'publish':
    case 'archive':
      handleTogglePublish(item)
      break
    case 'delete':
      handleDelete(item)
      break
  }
}

function handleManageTopics(scenario) {
  router.push({
    path: '/practice/topics',
    query: { scenario_id: scenario.id, scenario_title: scenario.title }
  })
}

function getDifficultyType(difficulty) {
  const map = { beginner: '', intermediate: 'warning', advanced: 'danger' }
  return map[difficulty] || 'info'
}

function getDifficultyLabel(difficulty) {
  const map = { beginner: '初级', intermediate: '中级', advanced: '高级' }
  return map[difficulty] || difficulty
}

function getStatusType(status) {
  const map = { published: 'success', draft: 'info', archived: 'danger' }
  return map[status] || 'info'
}

function getStatusLabel(status) {
  const map = { published: '已发布', draft: '草稿', archived: '已下架' }
  return map[status] || status
}

function formatNumber(num) {
  if (!num) return '0'
  if (num >= 10000) return (num / 10000).toFixed(1) + 'w'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toString()
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
.scenario-management {
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

.filter-bar {
  margin-bottom: 24px;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.text-right {
  text-align: right;
}

.loading-container {
  padding: 40px;
  background: #fff;
  border-radius: 8px;
}

.scenarios-grid {
  min-height: 400px;
}

.scenario-card {
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 20px;
  border: 1px solid #ebeef5;
}

.scenario-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.icon-wrapper {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  font-size: 28px;
}

.card-body .title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 10px 0;
  line-height: 1.4;
}

.card-body .description {
  color: #606266;
  font-size: 13px;
  line-height: 1.6;
  margin: 0 0 14px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}

.topic-count {
  background-color: #f0f9ff;
  border-color: #b3d8ff;
  color: #409eff;
}

.stats-row {
  display: flex;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 13px;
}

.stat-item .el-icon {
  font-size: 15px;
}

.stats-inline {
  font-size: 13px;
  color: #909399;
  white-space: nowrap;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding: 20px 0;
}

.emoji-picker {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 8px;
}

.emoji-item {
  font-size: 24px;
  cursor: pointer;
  padding: 8px;
  text-align: center;
  border-radius: 6px;
  transition: all 0.2s;
}

.emoji-item:hover {
  background: #f5f7fa;
  transform: scale(1.2);
}

.detail-content {
  padding: 0 20px;
}

.detail-stats {
  display: flex;
  gap: 24px;
}

.stat-box {
  text-align: center;
}

.stat-box .value {
  font-size: 28px;
  font-weight: 700;
  color: #409eff;
}

.stat-box .label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.topics-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.topic-tag {
  margin: 0;
}

.drawer-actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}
</style>
