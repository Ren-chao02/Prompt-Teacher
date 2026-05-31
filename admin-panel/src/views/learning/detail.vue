<template>
  <div class="learning-detail-container" v-loading="loading">
    <el-card v-if="materialData" shadow="never">
      <!-- 头部信息 -->
      <div class="detail-header">
        <div class="header-left">
          <el-button @click="$router.back()" :icon="ArrowLeft">返回列表</el-button>
        </div>
        
        <div class="header-center">
          <h1 class="title">{{ materialData.title }}</h1>
          <div class="meta-info">
            <el-tag :type="getCategoryTagType(materialData.category)" size="small">
              {{ getCategoryLabel(materialData.category) }}
            </el-tag>
            <el-tag :type="getStatusTagType(materialData.status)" size="small">
              {{ getStatusLabel(materialData.status) }}
            </el-tag>
          </div>
        </div>

        <div class="header-right">
          <el-button 
            type="primary" 
            v-if="canEdit"
            @click="handleEdit"
          >
            ✏️ 编辑
          </el-button>
          <el-dropdown trigger="click" v-if="isAdminOrTeacher">
            <el-button>
              更多操作
              <el-icon><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item 
                  v-if="canToggleStatus"
                  @click="handleToggleStatus"
                >
                  {{ materialData.status === 'published' ? '下架' : '发布' }}
                </el-dropdown-item>
                <el-dropdown-item 
                  v-if="isAdmin && canDelete"
                  divided
                  @click="handleDelete"
                >
                  🗑️ 删除
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 元信息卡片 -->
      <el-row :gutter="20" class="meta-cards">
        <el-col :span="6">
          <el-statistic title="阅读量" :value="materialData.view_count">
            <template #prefix>👁️</template>
          </el-statistic>
        </el-col>
        
        <el-col :span="6">
          <el-statistic title="点赞数" :value="materialData.like_count">
            <template #prefix>👍</template>
          </el-statistic>
        </el-col>
        
        <el-col :span="6">
          <el-statistic title="预计阅读" :value="materialData.reading_time" suffix="分钟">
            <template #prefix>⏱️</template>
          </el-statistic>
        </el-col>
        
        <el-col :span="6">
          <el-statistic title="排序权重" :value="materialData.order_index">
            <template #prefix>📊</template>
          </el-statistic>
        </el-col>
      </el-row>

      <!-- 作者和时间信息 -->
      <el-descriptions :column="3" border style="margin-bottom: 20px;">
        <el-descriptions-item label="作者">
          <span v-if="materialData.author_info">
            {{ materialData.author_info.username }}
            ({{ materialData.author_info.role }})
          </span>
          <span v-else>未知</span>
        </el-descriptions-item>
        
        <el-descriptions-item label="创建时间">
          {{ formatDate(materialData.created_at) }}
        </el-descriptions-item>
        
        <el-descriptions-item label="最后更新">
          {{ formatDate(materialData.updated_at) }}
        </el-descriptions-item>
        
        <el-descriptions-item label="发布时间" v-if="materialData.published_at">
          {{ formatDate(materialData.published_at) }}
        </el-descriptions-item>
        
        <el-descriptions-item label="标签" :span="2">
          <div class="tags-list">
            <el-tag
              v-for="(tag, index) in materialData.tags"
              :key="index"
              size="small"
              type="info"
              style="margin-right: 4px;"
            >
              {{ tag }}
            </el-tag>
            <span v-if="!materialData.tags || materialData.tags.length === 0" class="no-tags">
              暂无标签
            </span>
          </div>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 分割线 -->
      <el-divider />

      <!-- 内容区域 -->
      <div class="content-section">
        <h2 v-if="materialData.summary" class="summary-title">内容摘要</h2>
        <p v-if="materialData.summary" class="summary-content">{{ materialData.summary }}</p>

        <h2 class="content-title">详细内容</h2>
        <div class="markdown-body" v-html="renderedContent"></div>
      </div>
    </el-card>

    <!-- 空状态 -->
    <el-empty v-else-if="!loading" description="未找到该学习资料">
      <el-button type="primary" @click="$router.push('/learning/list')">
        返回列表
      </el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, ArrowDown } from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/modules/auth'
import { getMaterialDetail, deleteMaterial, publishMaterial, archiveMaterial } from '@/api/learning'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const materialData = ref(null)

const isAdmin = computed(() => authStore.isAdmin)
const isAdminOrTeacher = computed(() => authStore.isAdminOrTeacher)
const currentUser = computed(() => authStore.user)

const canEdit = computed(() => {
  if (!materialData.value) return false
  
  if (isAdmin.value) return true
  
  const isAuthor = materialData.value.author === currentUser.value?.id
  return isAdminOrTeacher.value && isAuthor
})

const canDelete = computed(() => isAdmin.value)

const canToggleStatus = computed(() => {
  if (!materialData.value) return false
  
  if (isAdmin.value) return true
  
  const isAuthor = materialData.value.author === currentUser.value?.id
  return isAdminOrTeacher.value && isAuthor
})

const renderedContent = computed(() => {
  if (!materialData.value?.content) return ''
  
  let content = materialData.value.content
  
  content = escapeHtml(content)
  content = renderMarkdown(content)
  
  return content
})

onMounted(() => {
  fetchMaterialDetail()
})

async function fetchMaterialDetail() {
  loading.value = true
  
  try {
    const res = await getMaterialDetail(route.params.id)
    materialData.value = res.data
    
    document.title = `${materialData.value.title} - Prompt Teacher 管理系统`
  } catch (error) {
    console.error('获取学习资料详情失败:', error)
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

function handleEdit() {
  router.push(`/learning/edit/${route.params.id}`)
}

async function handleToggleStatus() {
  const action = materialData.value.status === 'published' ? 'archive' : 'publish'
  const actionText = materialData.value.status === 'published' ? '下架' : '发布'
  
  try {
    await ElMessageBox.confirm(
      `确定要${actionText}《${materialData.value.title}》吗？`,
      '确认操作',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    
    if (action === 'publish') {
      await publishMaterial(route.params.id)
      ElMessage.success(`《${materialData.value.title}》已发布`)
    } else {
      await archiveMaterial(route.params.id)
      ElMessage.success(`《${materialData.value.title}》已下架`)
    }
    
    await fetchMaterialDetail()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
    }
  }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm(
      `确定要删除《${materialData.value.title}》吗？此操作不可恢复！`,
      '警告',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    
    await deleteMaterial(route.params.id)
    ElMessage.success('删除成功')
    
    router.push('/learning/list')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
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

function getCategoryLabel(category) {
  const map = {
    basic: '基础入门',
    intermediate: '进阶技巧',
    advanced: '高级应用',
    best_practices: '最佳实践'
  }
  return map[category] || category
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

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

function escapeHtml(text) {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

function renderMarkdown(content) {
  let html = content
  
  html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>')
  html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>')
  html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>')
  
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>')
  html = html.replace(/~~(.*?)~~/g, '<del>$1</del>')
  
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')
  
  html = html.replace(/^\s*[-*]\s+(.*$)/gim, '<li>$1</li>')
  html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
  
  html = html.replace(/^\s*\d+\.\s+(.*$)/gim, '<li>$1</li>')
  
  html = html.replace(/^\s*> (.*$)/gim, '<blockquote>$1</blockquote>')
  
  html = html.replace(/\n/gim, '<br>')
  
  return html
}
</script>

<style scoped>
.learning-detail-container {
  padding: 0;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.header-left,
.header-right {
  flex-shrink: 0;
}

.header-center {
  flex: 1;
  text-align: center;
  padding: 0 40px;
}

.title {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.meta-info {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.meta-cards {
  margin-bottom: 24px;
}

.content-section {
  max-width: 900px;
  margin: 0 auto;
}

.summary-title,
.content-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
  padding-top: 8px;
}

.summary-content {
  background-color: #f5f7fa;
  padding: 16px 20px;
  border-radius: 8px;
  line-height: 1.8;
  color: #606266;
  font-size: 15px;
  margin-bottom: 32px;
  border-left: 4px solid #409EFF;
}

.markdown-body {
  line-height: 1.8;
  color: #303133;
  font-size: 15px;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.markdown-body :deep(h1) {
  font-size: 28px;
  border-bottom: 2px solid #eaecef;
  padding-bottom: 8px;
}

.markdown-body :deep(h2) {
  font-size: 22px;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 6px;
}

.markdown-body :deep(h3) {
  font-size: 18px;
}

.markdown-body :deep(code) {
  background-color: #f5f7fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 14px;
  color: #e83e8c;
}

.markdown-body :deep(strong) {
  font-weight: 700;
  color: #1a1a1a;
}

.markdown-body :deep(blockquote) {
  border-left: 4px solid #409EFF;
  padding: 10px 20px;
  margin: 16px 0;
  background-color: #f5f7fa;
  color: #606266;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 30px;
  margin: 16px 0;
}

.markdown-body :deep(li) {
  margin: 6px 0;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.no-tags {
  color: #909399;
  font-size: 13px;
}
</style>
