<template>
  <div class="learning-detail-container" v-loading="loading">
    <!-- 顶部 Hero -->
    <div v-if="materialData" class="detail-hero" :style="heroStyle">
      <div class="hero-inner">
        <el-button class="back-btn" @click="$router.back()" :icon="ArrowLeft" round>
          返回
        </el-button>

        <div class="hero-tags">
          <el-tag :type="getCategoryTagType(materialData.category)" effect="dark" size="small">
            {{ materialData.category_display || getCategoryLabel(materialData.category) }}
          </el-tag>
          <el-tag
            v-if="materialData.status !== 'published'"
            :type="getStatusTagType(materialData.status)"
            effect="plain"
            size="small"
            class="status-tag"
          >
            {{ materialData.status_display || getStatusLabel(materialData.status) }}
          </el-tag>
        </div>

        <h1 class="hero-title">{{ materialData.title }}</h1>
        <p class="hero-summary">{{ materialData.summary || '暂无摘要' }}</p>

        <div class="hero-actions">
          <button
            class="hero-btn like"
            :class="{ active: materialData.is_liked }"
            @click="handleToggleLike"
            :title="materialData.is_liked ? '取消点赞' : '点赞'"
          >
            <el-icon><Star /></el-icon>
            <span class="num">{{ materialData.like_count || 0 }}</span>
            <span class="lbl">{{ materialData.is_liked ? '已点赞' : '点赞' }}</span>
          </button>

          <button
            class="hero-btn fav"
            :class="{ active: materialData.is_favorited }"
            @click="handleToggleFav"
            :title="materialData.is_favorited ? '取消收藏' : '收藏'"
          >
            <el-icon><CollectionTag /></el-icon>
            <span class="lbl">{{ materialData.is_favorited ? '已收藏' : '收藏' }}</span>
          </button>

          <button class="hero-btn share" @click="handleShare" title="复制链接">
            <el-icon><Share /></el-icon>
            <span class="lbl">分享</span>
          </button>

          <el-dropdown trigger="click" v-if="isAdminOrTeacher">
            <button class="hero-btn more">
              <el-icon><MoreFilled /></el-icon>
              <span class="lbl">更多</span>
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item
                  v-if="canEdit"
                  @click="handleEdit"
                >
                  <el-icon><Edit /></el-icon>编辑内容
                </el-dropdown-item>
                <el-dropdown-item
                  v-if="canToggleStatus"
                  @click="handleToggleStatus"
                >
                  <el-icon><Switch /></el-icon>
                  {{ materialData.status === 'published' ? '下架内容' : '发布内容' }}
                </el-dropdown-item>
                <el-dropdown-item
                  v-if="isAdmin && materialData"
                  divided
                  @click="handleDelete"
                >
                  <span style="color:#EF4444">
                    <el-icon><Delete /></el-icon>删除
                  </span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <div class="hero-meta">
          <span class="meta-pill">
            <el-icon><View /></el-icon>{{ formatNumber(materialData.view_count) }} 阅读
          </span>
          <span class="meta-pill">
            <el-icon><Clock /></el-icon>{{ materialData.reading_time || 1 }} 分钟
          </span>
          <span class="meta-pill" v-if="materialData.published_at">
            <el-icon><Calendar /></el-icon>{{ formatDate(materialData.published_at) }}
          </span>
        </div>
      </div>
    </div>

    <!-- 主体两栏 -->
    <div v-if="materialData" class="detail-body">
      <el-row :gutter="24">
        <!-- 左：内容 -->
        <el-col :xs="24" :md="16">
          <el-card shadow="never" class="content-card">
            <div class="markdown-body" v-html="renderedContent"></div>

            <div class="tag-section" v-if="materialData.tags && materialData.tags.length">
              <span class="tag-label">标签：</span>
              <span
                v-for="tag in materialData.tags"
                :key="tag"
                class="tag-chip"
                @click="handleTagClick(tag)"
              >#{{ tag }}</span>
            </div>

            <div class="action-bar">
              <button
                class="action-pill like"
                :class="{ active: materialData.is_liked }"
                @click="handleToggleLike"
              >
                <el-icon><Star /></el-icon>
                {{ materialData.is_liked ? '已点赞' : '点赞' }} ({{ materialData.like_count || 0 }})
              </button>
              <button
                class="action-pill fav"
                :class="{ active: materialData.is_favorited }"
                @click="handleToggleFav"
              >
                <el-icon><CollectionTag /></el-icon>
                {{ materialData.is_favorited ? '已收藏' : '收藏' }}
              </button>
            </div>
          </el-card>
        </el-col>

        <!-- 右：作者卡 + 信息 -->
        <el-col :xs="24" :md="8">
          <!-- 作者卡 -->
          <div v-if="materialData.author_info" class="author-card">
            <div class="author-cover" :style="getAuthorCoverStyle()"></div>
            <el-avatar
              :size="64"
              :src="materialData.author_info.avatar"
              class="author-avatar"
            >
              {{ (materialData.author_info.username || '匿').charAt(0).toUpperCase() }}
            </el-avatar>
            <div class="author-info">
              <h3 class="author-name">
                {{ materialData.author_info.username }}
                <el-tag size="small" effect="plain" :type="getRoleTagType(materialData.author_info.role)">
                  {{ getRoleLabel(materialData.author_info.role) }}
                </el-tag>
              </h3>
              <p class="author-bio">作者 · 创作了 {{ authorCount }} 篇内容</p>
            </div>

            <div class="author-stats">
              <div class="stat">
                <div class="stat-num">{{ authorCount }}</div>
                <div class="stat-lbl">作品</div>
              </div>
              <div class="stat-divider" />
              <div class="stat">
                <div class="stat-num">{{ formatNumber(materialData.view_count) }}</div>
                <div class="stat-lbl">阅读</div>
              </div>
              <div class="stat-divider" />
              <div class="stat">
                <div class="stat-num">{{ formatNumber(materialData.like_count) }}</div>
                <div class="stat-lbl">点赞</div>
              </div>
            </div>

            <el-button class="follow-btn" type="primary" round @click="handleFollow" v-if="!isAuthor">
              <el-icon><Plus /></el-icon>关注作者
            </el-button>
          </div>

          <!-- 文章信息卡 -->
          <el-card shadow="never" class="info-card">
            <template #header>
              <div class="info-header">
                <el-icon><InfoFilled /></el-icon>
                <span>文章信息</span>
              </div>
            </template>
            <ul class="info-list">
              <li>
                <span class="info-key">分类</span>
                <el-tag size="small" :type="getCategoryTagType(materialData.category)" effect="light">
                  {{ materialData.category_display || getCategoryLabel(materialData.category) }}
                </el-tag>
              </li>
              <li>
                <span class="info-key">状态</span>
                <el-tag size="small" :type="getStatusTagType(materialData.status)">
                  {{ materialData.status_display || getStatusLabel(materialData.status) }}
                </el-tag>
              </li>
              <li>
                <span class="info-key">阅读量</span>
                <span class="info-val">{{ materialData.view_count || 0 }}</span>
              </li>
              <li>
                <span class="info-key">点赞数</span>
                <span class="info-val">{{ materialData.like_count || 0 }}</span>
              </li>
              <li>
                <span class="info-key">预计用时</span>
                <span class="info-val">{{ materialData.reading_time || 1 }} 分钟</span>
              </li>
              <li>
                <span class="info-key">排序权重</span>
                <span class="info-val">{{ materialData.order_index }}</span>
              </li>
              <li>
                <span class="info-key">创建时间</span>
                <span class="info-val">{{ formatDate(materialData.created_at) }}</span>
              </li>
              <li>
                <span class="info-key">更新时间</span>
                <span class="info-val">{{ formatDate(materialData.updated_at) }}</span>
              </li>
            </ul>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 空 -->
    <el-empty v-else-if="!loading" description="未找到该学习资料">
      <el-button type="primary" @click="$router.push('/learning/list')">返回列表</el-button>
    </el-empty>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Star,
  CollectionTag,
  Share,
  View,
  Clock,
  Calendar,
  Edit,
  Delete,
  MoreFilled,
  Switch,
  InfoFilled,
  Plus
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/store/modules/auth'
import {
  getMaterialDetail,
  deleteMaterial,
  publishMaterial,
  archiveMaterial,
  toggleLike,
  toggleFavorite,
  getMyMaterials
} from '@/api/learning'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const materialData = ref(null)
const authorCount = ref(0)

const isAdmin = computed(() => authStore.isAdmin)
const isAdminOrTeacher = computed(() => authStore.isAdminOrTeacher)
const currentUser = computed(() => authStore.user)
const isAuthor = computed(() => materialData.value && currentUser.value
  && materialData.value.author === currentUser.value.id)

const canEdit = computed(() => {
  if (!materialData.value) return false
  if (isAdmin.value) return true
  return isAdminOrTeacher.value && isAuthor.value
})

const canDelete = computed(() => isAdmin.value)

const canToggleStatus = computed(() => {
  if (!materialData.value) return false
  if (isAdmin.value) return true
  return isAdminOrTeacher.value && isAuthor.value
})

const heroStyle = computed(() => {
  const colors = {
    basic: 'linear-gradient(135deg, #1E3A8A 0%, #2563EB 60%, #60A5FA 100%)',
    intermediate: 'linear-gradient(135deg, #92400E 0%, #D97706 60%, #FBBF24 100%)',
    advanced: 'linear-gradient(135deg, #991B1B 0%, #DC2626 60%, #F87171 100%)',
    best_practices: 'linear-gradient(135deg, #065F46 0%, #10B981 60%, #6EE7B7 100%)'
  }
  return {
    background: colors[materialData.value?.category] || colors.basic
  }
})

const renderedContent = computed(() => {
  if (!materialData.value?.content) return '<p style="color:#9CA3AF;text-align:center;padding:40px 0">暂无内容</p>'
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
    materialData.value = res.data.data || res.data
    document.title = `${materialData.value.title} - Prompt Teacher`
    fetchAuthorCount()
  } catch (error) {
    console.error('获取详情失败:', error)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

async function fetchAuthorCount() {
  if (!materialData.value?.author_info?.id) return
  try {
    const res = await getMyMaterials({ author: materialData.value.author_info.id, page_size: 1 })
    const data = res.data.data || res.data
    authorCount.value = data.count || (Array.isArray(data) ? data.length : 0)
  } catch (e) {
    authorCount.value = 1
  }
}

async function handleToggleLike() {
  if (!currentUser.value) {
    ElMessage.warning('请先登录')
    return
  }
  try {
    const res = await toggleLike(route.params.id)
    const result = res.data.data || res.data
    materialData.value.is_liked = result.liked
    materialData.value.like_count = result.like_count
    ElMessage.success(result.liked ? '已点赞 ⭐' : '已取消点赞')
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

async function handleToggleFav() {
  if (!currentUser.value) {
    ElMessage.warning('请先登录')
    return
  }
  try {
    const res = await toggleFavorite(route.params.id)
    const result = res.data.data || res.data
    materialData.value.is_favorited = result.favorited
    ElMessage.success(result.favorited ? '已加入我的收藏' : '已取消收藏')
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

function handleShare() {
  const url = window.location.href
  if (navigator.clipboard) {
    navigator.clipboard.writeText(url).then(() => ElMessage.success('链接已复制'))
  } else {
    ElMessage.info(url)
  }
}

function handleFollow() {
  ElMessage.success(`已关注 ${materialData.value.author_info.username}`)
}

function handleTagClick(tag) {
  router.push({ path: '/learning/list', query: { tag } })
}

function handleEdit() {
  router.push(`/learning/edit/${route.params.id}`)
}

async function handleToggleStatus() {
  const isPublished = materialData.value.status === 'published'
  const actionText = isPublished ? '下架' : '发布'
  try {
    await ElMessageBox.confirm(
      `确定要${actionText}《${materialData.value.title}》吗？`,
      '确认操作',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    if (isPublished) {
      await archiveMaterial(route.params.id)
    } else {
      await publishMaterial(route.params.id)
    }
    ElMessage.success(`已${actionText}`)
    await fetchMaterialDetail()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
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
    ElMessage.success('已删除')
    router.push('/learning/list')
  } catch (e) {
    if (e !== 'cancel') console.error(e)
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
function getRoleLabel(r) {
  return { admin: '管理员', teacher: '教师', student: '学生' }[r] || r
}
function getRoleTagType(r) {
  return { admin: 'danger', teacher: 'warning', student: 'success' }[r] || 'info'
}
function getAuthorCoverStyle() {
  return {
    background: 'linear-gradient(135deg, #6366F1 0%, #8B5CF6 50%, #EC4899 100%)'
  }
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
  html = html.replace(/(<li>[\s\S]*?<\/li>)(?=\s*(?:<li>|$))/g, '<ul>$1</ul>')
  html = html.replace(/^\s*> (.*$)/gim, '<blockquote>$1</blockquote>')
  html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
  html = html.replace(/\n/g, '<br>')
  return html
}
</script>

<style scoped>
.learning-detail-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Hero */
.detail-hero {
  border-radius: 18px;
  color: #ffffff;
  position: relative;
  overflow: hidden;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

.detail-hero::before {
  content: '';
  position: absolute;
  top: -40%;
  right: -10%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
  pointer-events: none;
}

.hero-inner {
  padding: 32px 36px 28px;
  position: relative;
  z-index: 1;
}

.back-btn {
  position: absolute;
  top: 24px;
  left: 24px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #ffffff;
  backdrop-filter: blur(8px);
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  color: #ffffff;
}

.hero-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.hero-title {
  font-size: 30px;
  font-weight: 700;
  margin: 0 0 12px;
  line-height: 1.3;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.hero-summary {
  font-size: 15px;
  line-height: 1.7;
  opacity: 0.92;
  margin: 0 0 24px;
  max-width: 720px;
}

.hero-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.hero-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.25);
  border-radius: 999px;
  color: #ffffff;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  backdrop-filter: blur(8px);
  font-family: inherit;
}

.hero-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
}

.hero-btn .num {
  font-weight: 700;
  margin: 0 2px;
}

.hero-btn.active {
  background: rgba(255, 255, 255, 0.95);
  color: #2563EB;
  border-color: rgba(255, 255, 255, 0.95);
}

.hero-btn.like.active { color: #F59E0B; }
.hero-btn.fav.active { color: #EC4899; }

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.meta-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 999px;
  font-size: 12px;
  backdrop-filter: blur(8px);
}

/* 主体 */
.detail-body {
  margin-top: 4px;
}

.content-card :deep(.el-card__body) {
  padding: 32px 36px;
}

.markdown-body {
  line-height: 1.85;
  color: #1F2937;
  font-size: 15px;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  margin: 28px 0 14px;
  font-weight: 600;
  color: #111827;
}

.markdown-body :deep(h1) {
  font-size: 26px;
  border-bottom: 2px solid #E5E7EB;
  padding-bottom: 8px;
}

.markdown-body :deep(h2) {
  font-size: 22px;
  border-bottom: 1px solid #E5E7EB;
  padding-bottom: 6px;
}

.markdown-body :deep(h3) { font-size: 18px; }

.markdown-body :deep(code) {
  background: #F3F4F6;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  color: #DB2777;
}

.markdown-body :deep(pre) {
  background: #1F2937;
  color: #F9FAFB;
  padding: 16px 20px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 16px 0;
}

.markdown-body :deep(pre) code {
  background: transparent;
  color: inherit;
  padding: 0;
}

.markdown-body :deep(strong) { color: #111827; font-weight: 600; }

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 24px;
  margin: 12px 0;
}

.markdown-body :deep(li) {
  margin: 4px 0;
}

.markdown-body :deep(blockquote) {
  border-left: 4px solid #3B82F6;
  background: #EFF6FF;
  padding: 12px 18px;
  margin: 16px 0;
  color: #1E40AF;
  border-radius: 0 6px 6px 0;
}

.tag-section {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #F3F4F6;
}

.tag-label {
  font-size: 13px;
  color: #6B7280;
  font-weight: 500;
}

.tag-chip {
  display: inline-block;
  padding: 4px 12px;
  background: #F3F4F6;
  color: #4B5563;
  border-radius: 999px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.tag-chip:hover {
  background: #2563EB;
  color: #ffffff;
}

.action-bar {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #F3F4F6;
}

.action-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 28px;
  background: #F9FAFB;
  border: 1px solid #E5E7EB;
  border-radius: 999px;
  font-size: 14px;
  color: #4B5563;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}

.action-pill:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
}

.action-pill.like.active {
  background: #FEF3C7;
  color: #D97706;
  border-color: #FCD34D;
}

.action-pill.fav.active {
  background: #FCE7F3;
  color: #BE185D;
  border-color: #F9A8D4;
}

/* 右侧作者卡 */
.author-card {
  position: relative;
  background: #ffffff;
  border-radius: 14px;
  padding: 60px 24px 24px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  margin-bottom: 16px;
  border: 1px solid #F3F4F6;
}

.author-cover {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 80px;
  border-radius: 14px 14px 0 0;
}

.author-avatar {
  position: relative;
  z-index: 1;
  background: #ffffff;
  color: #6366F1;
  font-weight: 700;
  font-size: 26px;
  border: 4px solid #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.author-info {
  margin-top: 8px;
}

.author-name {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 4px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.author-bio {
  font-size: 13px;
  color: #6B7280;
  margin: 0;
}

.author-stats {
  display: flex;
  align-items: center;
  justify-content: space-around;
  margin: 20px 0;
  padding: 16px 0;
  background: #F9FAFB;
  border-radius: 10px;
}

.author-stats .stat {
  text-align: center;
  flex: 1;
}

.author-stats .stat-num {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
}

.author-stats .stat-lbl {
  font-size: 12px;
  color: #6B7280;
  margin-top: 2px;
}

.stat-divider {
  width: 1px;
  height: 24px;
  background: #E5E7EB;
}

.follow-btn {
  width: 100%;
}

/* 信息卡 */
.info-card {
  border-radius: 14px;
}

.info-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: #111827;
}

.info-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.info-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #F3F4F6;
  font-size: 13px;
}

.info-list li:last-child {
  border-bottom: none;
}

.info-key {
  color: #6B7280;
}

.info-val {
  color: #111827;
  font-weight: 500;
}

/* 响应式 */
@media (max-width: 992px) {
  .hero-inner { padding: 60px 20px 24px; }
  .hero-title { font-size: 24px; }
  .content-card :deep(.el-card__body) { padding: 24px 20px; }
}
</style>
