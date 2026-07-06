<template>
  <div class="topic-management">
    <div class="page-header">
      <div class="header-left">
        <el-button text @click="$router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回场景
        </el-button>
        <h2>主题管理</h2>
        <el-tag v-if="currentScenario" type="info" size="large">
          {{ currentScenario.title }}
        </el-tag>
      </div>
      
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建主题
      </el-button>
    </div>

    <div class="scenario-selector" v-if="!route.query.scenario_id">
      <el-select
        v-model="selectedScenarioId"
        placeholder="选择要管理的场景"
        style="width: 100%; max-width: 500px;"
        @change="loadTopics"
      >
        <el-option
          v-for="s in scenarios"
          :key="s.id"
          :label="`${s.icon} ${s.title}`"
          :value="s.id"
        />
      </el-select>
    </div>

    <div v-if="loading && topics.length === 0" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="topics.length > 0 || selectedScenarioId" class="topics-container">
      <!-- 统计卡片 -->
      <el-row :gutter="16" class="stats-row">
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-value">{{ topics.length }}</div>
              <div class="stat-label">总主题数</div>
            </div>
            <el-icon class="stat-icon"><Document /></el-icon>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card success">
            <div class="stat-content">
              <div class="stat-value">{{ activeCount }}</div>
              <div class="stat-label">已启用</div>
            </div>
            <el-icon class="stat-icon"><CircleCheck /></el-icon>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card warning">
            <div class="stat-content">
              <div class="stat-value">{{ standardCount }}</div>
              <div class="stat-label">标准题</div>
            </div>
            <el-icon class="stat-icon"><EditPen /></el-icon>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card danger">
            <div class="stat-content">
              <div class="stat-value">{{ challengeCount }}</div>
              <div class="stat-label">挑战题</div>
            </div>
            <el-icon class="stat-icon"><TrophyBase /></el-icon>
          </el-card>
        </el-col>
      </el-row>

      <!-- 主题列表 -->
      <el-table :data="topics" stripe border class="topics-table">
        <el-table-column type="index" label="#" width="60" align="center" />
        
        <el-table-column prop="topic_number" label="编号" width="80" align="center">
          <template #default="{ row }">
            <el-tag type="primary" round>主题 {{ row.topic_number }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        
        <el-table-column prop="topic_type" label="类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getTopicTypeType(row.topic_type)" size="small">
              {{ getTopicTypeLabel(row.topic_type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="评分设置" width="180" align="center">
          <template #default="{ row }">
            <span class="score-info">
              满分: <strong>{{ row.max_score }}</strong><br/>
              时限: <strong>{{ row.time_limit_minutes }}分钟</strong>
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="is_active" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              v-model="row.is_active"
              @change="(val) => handleToggleActive(row, val)"
              :active-text="'启用'"
              :inactive-text="'禁用'"
            />
          </template>
        </el-table-column>
        
        <el-table-column prop="order" label="排序" width="100" align="center">
          <template #default="{ row }">
            <el-input-number
              v-model="row.order"
              :min="0"
              :max="999"
              size="small"
              @change="(val) => handleUpdateOrder(row, val)"
            />
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="220" fixed="right" align="center">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="handleView(row)">查看</el-button>
            <el-button text type="warning" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm
              title="确定删除此主题？"
              confirm-button-text="确定"
              cancel-button-text="取消"
              @confirm="handleDelete(row)"
            >
              <template #reference>
                <el-button text type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-empty v-else description="请先选择一个场景或创建新主题" />

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      destroy-on-close
      top="5vh"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
        label-position="top"
      >
        <el-tabs v-model="activeTab">
          <el-tab-pane label="基本信息" name="basic">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="所属场景" prop="scenario">
                  <el-select
                    v-model="formData.scenario"
                    placeholder="选择场景"
                    :disabled="!!editingId || !!selectedScenarioId"
                  >
                    <el-option
                      v-for="s in scenarios"
                      :key="s.id"
                      :label="s.title"
                      :value="s.id"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="主题编号" prop="topic_number">
                  <el-input-number
                    v-model="formData.topic_number"
                    :min="1"
                    :max="10"
                    placeholder="1 或 2"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="主题标题" prop="title">
              <el-input
                v-model="formData.title"
                placeholder="输入主题标题"
                maxlength="200"
                show-word-limit
              />
            </el-form-item>

            <el-form-item label="主题描述" prop="description">
              <el-input
                v-model="formData.description"
                type="textarea"
                :rows="3"
                placeholder="描述这个练习主题的目标和要求..."
                maxlength="500"
                show-word-limit
              />
            </el-form-item>

            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="题目类型" prop="topic_type">
                  <el-select v-model="formData.topic_type" placeholder="选择类型">
                    <el-option label="标准题" value="standard" />
                    <el-option label="挑战题" value="challenge" />
                    <el-option label="加分题" value="bonus" />
                  </el-select>
                </el-form-item>
              </el-col>
              
              <el-col :span="8">
                <el-form-item label="满分" prop="max_score">
                  <el-input-number
                    v-model="formData.max_score"
                    :min="1"
                    :max="200"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :span="8">
                <el-form-item label="时间限制(分钟)" prop="time_limit_minutes">
                  <el-input-number
                    v-model="formData.time_limit_minutes"
                    :min="5"
                    :max="120"
                    :step="5"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="排序权重" prop="order">
                  <el-input-number v-model="formData.order" :min="0" :max="999" />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-form-item label="启用状态">
                  <el-switch v-model="formData.is_active" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>

          <el-tab-pane label="示例提示词" name="example">
            <el-form-item label="示例提示词 (可选)">
              <el-input
                v-model="formData.example_prompt"
                type="textarea"
                :rows="8"
                placeholder="提供一个示例提示词，帮助用户理解题目要求..."
                show-word-limit
              />
            </el-form-item>
          </el-tab-pane>

          <el-tab-pane label="评估标准 (JSON)" name="criteria">
            <el-alert
              title="评估标准格式说明"
              type="info"
              :closable="false"
              show-icon
              style="margin-bottom: 16px;"
            >
              <template #default>
                <pre style="margin: 8px 0; font-size: 13px;">{
  "criteria": [
    {"name": "准确性", "description": "回答的准确程度", "weight": 30},
    {"name": "完整性", "description": "是否覆盖所有要点", "weight": 25},
    {"name": "逻辑性", "description": "思路是否清晰", "weight": 25},
    {"name": "表达质量", "description": "语言组织能力", "weight": 20}
  ],
  "weights": {
    "accuracy": 30,
    "completeness": 25,
    "logic": 25,
    "expression": 20
  }
}</pre>
              </template>
            </el-alert>

            <el-form-item label="评估标准 JSON">
              <el-input
                v-model="criteriaJson"
                type="textarea"
                :rows="15"
                placeholder='{"criteria": [...], "weights": {...}}'
                :class="{ 'json-error': jsonError }"
              />
              <div v-if="jsonError" class="error-message">
                <el-icon color="#f56c6c"><WarningFilled /></el-icon>
                {{ jsonError }}
              </div>
            </el-form-item>
          </el-tab-pane>
        </el-tabs>
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
      :title="`主题详情 - ${currentTopic?.title}`"
      size="650px"
      direction="rtl"
    >
      <template v-if="currentTopic">
        <div class="detail-content">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="编号">
              <el-tag type="primary" round>主题 {{ currentTopic.topic_number }}</el-tag>
            </el-descriptions-item>
            
            <el-descriptions-item label="标题">
              {{ currentTopic.title }}
            </el-descriptions-item>
            
            <el-descriptions-item label="描述">
              {{ currentTopic.description }}
            </el-descriptions-item>
            
            <el-descriptions-item label="类型">
              <el-tag :type="getTopicTypeType(currentTopic.topic_type)">
                {{ getTopicTypeLabel(currentTopic.topic_type) }}
              </el-tag>
            </el-descriptions-item>
            
            <el-descriptions-item label="评分设置">
              <div class="score-detail">
                <el-tag effect="plain">满分: {{ currentTopic.max_score }}分</el-tag>
                <el-tag effect="plain">时限: {{ currentTopic.time_limit_minutes }}分钟</el-tag>
              </div>
            </el-descriptions-item>
            
            <el-descriptions-item label="状态">
              <el-tag :type="currentTopic.is_active ? 'success' : 'danger'">
                {{ currentTopic.is_active ? '已启用' : '已禁用' }}
              </el-tag>
            </el-descriptions-item>
            
            <el-descriptions-item label="示例提示词">
              <div v-if="currentTopic.example_prompt" class="example-prompt">
                {{ currentTopic.example_prompt }}
              </div>
              <span v-else class="text-muted">未提供</span>
            </el-descriptions-item>
            
            <el-descriptions-item label="评估标准">
              <div v-if="currentTopic.evaluation_criteria && Object.keys(currentTopic.evaluation_criteria).length" class="criteria-display">
                <pre>{{ formatJson(currentTopic.evaluation_criteria) }}</pre>
              </div>
              <span v-else class="text-muted">未配置</span>
            </el-descriptions-item>
            
            <el-descriptions-item label="时间信息">
              创建: {{ formatDate(currentTopic.created_at) }}<br/>
              更新: {{ formatDate(currentTopic.updated_at) }}
            </el-descriptions-item>
          </el-descriptions>

          <div class="drawer-actions">
            <el-button type="primary" @click="handleEditFromDrawer">编辑主题</el-button>
          </div>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, ArrowLeft, Document, CircleCheck, EditPen,
  TrophyBase, WarningFilled
} from '@element-plus/icons-vue'
import {
  getScenarioList,
  getTopicsByScenario,
  getTopicList,
  getTopicDetail,
  createTopic,
  updateTopic,
  deleteTopic
} from '@/api/practice'

const route = useRoute()

const loading = ref(false)
const scenarios = ref([])
const topics = ref([])
const selectedScenarioId = ref(null)
const currentScenario = ref(null)

const dialogVisible = ref(false)
const drawerVisible = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const formRef = ref(null)
const currentTopic = ref(null)
const activeTab = ref('basic')
const criteriaJson = ref('')
const jsonError = ref('')

const formData = reactive({
  scenario: null,
  topic_number: 1,
  title: '',
  description: '',
  topic_type: 'standard',
  example_prompt: '',
  evaluation_criteria: {},
  max_score: 100,
  time_limit_minutes: 30,
  order: 0,
  is_active: true
})

const formRules = {
  scenario: [{ required: true, message: '请选择所属场景', trigger: 'change' }],
  topic_number: [{ required: true, message: '请输入主题编号', trigger: 'blur' }],
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 2, max: 200, message: '长度在2到200个字符之间', trigger: 'blur' }
  ],
  topic_type: [{ required: true, message: '请选择题目类型', trigger: 'change' }],
  max_score: [{ required: true, message: '请输入满分', trigger: 'blur' }]
}

const activeCount = computed(() => topics.value.filter(t => t.is_active).length)
const standardCount = computed(() => topics.value.filter(t => t.topic_type === 'standard').length)
const challengeCount = computed(() => topics.value.filter(t => t.topic_type === 'challenge').length)

onMounted(async () => {
  await loadScenarios()
  
  if (route.query.scenario_id) {
    selectedScenarioId.value = parseInt(route.query.scenario_id)
    
    const scenario = scenarios.value.find(s => s.id === selectedScenarioId.value)
    if (scenario) {
      currentScenario.value = scenario
    }
    
    await loadTopics()
  }
})

watch(criteriaJson, (newVal) => {
  if (!newVal) {
    jsonError.value = ''
    return
  }
  
  try {
    const parsed = JSON.parse(newVal)
    formData.evaluation_criteria = parsed
    jsonError.value = ''
  } catch (e) {
    jsonError.value = `JSON 格式错误: ${e.message}`
  }
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

async function loadTopics() {
  if (!selectedScenarioId.value) return
  
  loading.value = true
  
  try {
    const res = await getTopicsByScenario(selectedScenarioId.value)
    
    if (res.code === 200) {
      topics.value = res.data || []
    }
  } catch (error) {
    console.error('加载主题列表失败:', error)
  } finally {
    loading.value = false
  }
}

function getDialogTitle() {
  return editingId.value ? '编辑主题' : '新建主题'
}

function resetForm() {
  Object.assign(formData, {
    scenario: selectedScenarioId.value || null,
    topic_number: 1,
    title: '',
    description: '',
    topic_type: 'standard',
    example_prompt: '',
    evaluation_criteria: {},
    max_score: 100,
    time_limit_minutes: 30,
    order: 0,
    is_active: true
  })
  criteriaJson.value = ''
  jsonError.value = ''
  editingId.value = null
  activeTab.value = 'basic'
}

function handleCreate() {
  resetForm()
  dialogVisible.value = true
}

function handleEdit(item) {
  editingId.value = item.id
  
  Object.assign(formData, {
    scenario: item.scenario,
    topic_number: item.topic_number,
    title: item.title,
    description: item.description,
    topic_type: item.topic_type,
    example_prompt: item.example_prompt || '',
    evaluation_criteria: item.evaluation_criteria || {},
    max_score: item.max_score,
    time_limit_minutes: item.time_limit_minutes,
    order: item.order,
    is_active: item.is_active
  })
  
  criteriaJson.value = item.evaluation_criteria 
    ? JSON.stringify(item.evaluation_criteria, null, 2) 
    : ''
  
  dialogVisible.value = true
}

function handleEditFromDrawer() {
  drawerVisible.value = false
  handleEdit(currentTopic.value)
}

function handleView(item) {
  currentTopic.value = item
  drawerVisible.value = true
}

async function handleSubmit() {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  
  if (jsonError.value) {
    ElMessage.error('请修正 JSON 格式错误')
    activeTab.value = 'criteria'
    return
  }
  
  submitting.value = true
  
  try {
    let res
    if (editingId.value) {
      res = await updateTopic(editingId.value, formData)
      ElMessage.success('主题更新成功')
    } else {
      res = await createTopic(formData)
      ElMessage.success('主题创建成功')
    }
    
    dialogVisible.value = false
    loadTopics()
  } catch (error) {
    console.error('保存失败:', error)
  } finally {
    submitting.value = false
  }
}

async function handleDelete(item) {
  try {
    await deleteTopic(item.id)
    ElMessage.success('删除成功')
    loadTopics()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

async function handleToggleActive(item, value) {
  try {
    await updateTopic(item.id, { ...item, is_active: value })
    ElMessage.success(value ? '已启用' : '已禁用')
  } catch (error) {
    item.is_active = !value
    console.error('更新失败:', error)
  }
}

async function handleUpdateOrder(item, value) {
  try {
    await updateTopic(item.id, { ...item, order: value })
  } catch (error) {
    console.error('更新排序失败:', error)
  }
}

function getTopicTypeType(type) {
  const map = { standard: '', challenge: 'warning', bonus: 'success' }
  return map[type] || 'info'
}

function getTopicTypeLabel(type) {
  const map = { standard: '标准题', challenge: '挑战题', bonus: '加分题' }
  return map[type] || type
}

function formatJson(obj) {
  return JSON.stringify(obj, null, 2)
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
.topic-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h2 {
  margin: 0;
  font-size: 22px;
  color: #303133;
}

.scenario-selector {
  max-width: 500px;
  margin-bottom: 24px;
}

.loading-container {
  padding: 40px;
  background: #fff;
  border-radius: 8px;
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

.topics-container {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.topics-table {
  margin-top: 16px;
}

.score-info {
  font-size: 13px;
  line-height: 1.6;
  color: #606266;
}

.detail-content {
  padding: 0 20px;
}

.score-detail {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.example-prompt {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.criteria-display pre {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.text-muted {
  color: #c0c4cc;
}

.json-error :deep(.el-textarea__inner) {
  border-color: #f56c6c;
}

.error-message {
  margin-top: 8px;
  font-size: 13px;
  color: #f56c6c;
  display: flex;
  align-items: center;
  gap: 4px;
}

.drawer-actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}
</style>
