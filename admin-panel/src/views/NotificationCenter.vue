<template>
  <div class="notification-center">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>消息通知</h2>
      <div class="header-actions">
        <el-button
          v-if="hasUnread"
          type="primary"
          @click="handleMarkAllRead"
          :loading="markingAllRead"
        >
          全部标记已读
        </el-button>
        <el-tag v-if="hasUnread" type="danger" effect="dark" round>
          {{ unreadCount }} 条未读
        </el-tag>
      </div>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6" v-for="(stat, index) in typeStats" :key="index">
        <el-card shadow="hover" class="stat-card" :class="[`type-${stat.type}`]">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="28">
                <component :is="stat.icon" />
              </el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-count">{{ stat.count }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 筛选和搜索 -->
    <div class="filter-bar">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="系统通知" name="system" />
        <el-tab-pane label="学习任务" name="learning" />
        <el-tab-pane label="练习成绩" name="practice" />
        <el-tab-pane label="互动消息" name="interaction" />
      </el-tabs>

      <div class="filter-actions">
        <el-select 
          v-model="filters.priority" 
          placeholder="优先级筛选" 
          clearable
          size="default"
          style="width: 140px;"
          @change="handleFilterChange"
        >
          <el-option label="全部优先级" value="" />
          <el-option label="紧急" value="urgent" />
          <el-option label="高" value="high" />
          <el-option label="中" value="medium" />
          <el-option label="低" value="low" />
        </el-select>

        <el-input
          v-model="filters.search"
          placeholder="搜索通知..."
          prefix-icon="Search"
          clearable
          size="default"
          style="width: 240px;"
          @input="debounceSearch"
        />
      </div>
    </div>

    <!-- 通知列表 -->
    <div class="notification-list-container">
      <!-- 加载状态 -->
      <div v-if="loading && notifications.length === 0" class="loading-state">
        <el-skeleton :rows="5" animated />
      </div>

      <!-- 空状态 -->
      <div v-else-if="notifications.length === 0" class="empty-state">
        <el-empty description="暂无通知消息" :image-size="200">
          <template #description>
            <p>您目前没有任何{{ activeTab === 'all' ? '' : typeLabels[activeTab] }}通知</p>
          </template>
        </el-empty>
      </div>

      <!-- 通知列表 -->
      <transition-group v-else name="list" tag="div" class="notification-list">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="notification-card"
          :class="{ 
            unread: !notification.is_read,
            [`priority-${notification.priority}`]: true
          }"
          @click="handleNotificationClick(notification)"
        >
          <!-- 左侧图标区域 -->
          <div class="card-left">
            <div 
              class="notification-type-badge"
              :class="[`type-${notification.notification_type}`, `priority-${notification.priority}`]"
            >
              <el-icon :size="20">
                <component :is="getTypeIcon(notification.notification_type)" />
              </el-icon>
            </div>

            <!-- 未读指示器 -->
            <div v-if="!notification.is_read" class="unread-indicator" />
          </div>

          <!-- 中间内容区域 -->
          <div class="card-content">
            <div class="card-header">
              <h4 class="card-title">{{ notification.title }}</h4>
              <el-tag 
                :type="getPriorityTagType(notification.priority)"
                size="small"
                round
                effect="light"
              >
                {{ getPriorityLabel(notification.priority) }}
              </el-tag>
            </div>

            <p class="card-description">{{ stripHtml(notification.content) }}</p>

            <div class="card-meta">
              <span class="meta-time">
                <el-icon><Clock /></el-icon>
                {{ notification.time_ago || formatTime(notification.created_at) }}
              </span>
              
              <span v-if="notification.sender_info" class="meta-sender">
                来自: {{ notification.sender_info.username }}
              </span>
            </div>
          </div>

          <!-- 右侧操作区域 -->
          <div class="card-actions">
            <el-button
              v-if="!notification.is_read"
              link
              type="primary"
              size="small"
              @click.stop="handleMarkRead(notification.id)"
            >
              标记已读
            </el-button>

            <el-button
              v-if="notification.link"
              link
              type="info"
              size="small"
              @click.stop="handleGoToLink(notification.link)"
            >
              查看详情 →
            </el-button>
          </div>
        </div>
      </transition-group>

      <!-- 分页 -->
      <div v-if="total > pageSize" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next, jumper, total"
          background
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 通知详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="通知详情"
      width="600px"
      destroy-on-close
    >
      <div v-if="selectedNotification" class="notification-detail">
        <div class="detail-header">
          <div class="detail-type" :class="`type-${selectedNotification.notification_type}`">
            <el-icon :size="24">
              <component :is="getTypeIcon(selectedNotification.notification_type)" />
            </el-icon>
          </div>
          <div class="detail-title-section">
            <h3>{{ selectedNotification.title }}</h3>
            <div class="detail-meta">
              <el-tag :type="getPriorityTagType(selectedNotification.priority)" size="small">
                {{ getPriorityLabel(selectedNotification.priority) }}
              </el-tag>
              <span>{{ selectedNotification.time_ago }}</span>
            </div>
          </div>
        </div>

        <el-divider />

        <div class="detail-content" v-html="selectedNotification.content" />

        <div class="detail-footer">
          <el-button
            v-if="!selectedNotification.is_read"
            type="primary"
            @click="handleMarkRead(selectedNotification.id); showDetailDialog = false"
          >
            标记为已读
          </el-button>
          
          <el-button
            v-if="selectedNotification.link"
            type="primary"
            plain
            @click="handleGoToLink(selectedNotification.link); showDetailDialog = false"
          >
            查看详情
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationsStore } from '@/stores/notifications'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Clock, Search, InfoFilled, Document, Trophy, 
  ChatDotRound, Warning, Bell 
} from '@element-plus/icons-vue'

const router = useRouter()
const notificationsStore = useNotificationsStore()

// 响应式数据
const loading = ref(false)
const markingAllRead = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const activeTab = ref('all')
const showDetailDialog = ref(false)
const selectedNotification = ref(null)

// 筛选条件
const filters = ref({
  search: '',
  priority: ''
})

// 类型标签映射
const typeLabels = {
  all: '',
  system: '系统',
  learning: '学习任务',
  practice: '练习成绩',
  interaction: '互动消息'
}

// 计算属性
const notifications = computed(() => notificationsStore.notifications)
const unreadCount = computed(() => notificationsStore.unreadCount)
const hasUnread = computed(() => notificationsStore.hasUnread)

const typeStats = computed(() => {
  const breakdown = notificationsStore.unreadBreakdown
  
  return [
    {
      type: 'all',
      label: '全部通知',
      count: unreadCount.value,
      icon: Bell
    },
    {
      type: 'system',
      label: '系统通知',
      count: breakdown.system || 0,
      icon: InfoFilled
    },
    {
      type: 'learning',
      label: '学习任务',
      count: breakdown.learning || 0,
      icon: Document
    },
    {
      type: 'practice',
      label: '练习成绩',
      count: breakdown.practice || 0,
      icon: Trophy
    }
  ]
})

// 图标映射函数
function getTypeIcon(type) {
  const iconMap = {
    system: InfoFilled,
    learning: Document,
    practice: Trophy,
    interaction: ChatDotRound,
    announcement: Warning
  }
  return iconMap[type] || InfoFilled
}

function getPriorityTagType(priority) {
  const map = {
    urgent: 'danger',
    high: 'warning',
    medium: 'info',
    low: 'info'
  }
  return map[priority] || 'info'
}

function getPriorityLabel(priority) {
  const map = {
    urgent: '紧急',
    high: '高',
    medium: '中',
    low: '低'
  }
  return map[priority] || '未知'
}

// 工具函数
function formatTime(timeStr) {
  if (!timeStr) return ''
  
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function stripHtml(html) {
  if (!html) return ''
  return html.replace(/<[^>]+>/g, '').substring(0, 150)
}

let searchTimeout = null
function debounceSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    handleFilterChange()
  }, 500)
}

// 数据加载方法
async function loadNotifications() {
  loading.value = true
  
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    // 类型筛选
    if (activeTab.value !== 'all') {
      params.notification_type = activeTab.value
    }

    // 优先级筛选
    if (filters.value.priority) {
      params.priority = filters.value.priority
    }

    // 搜索关键词
    if (filters.value.search) {
      params.search = filters.value.search
    }

    const result = await notificationsStore.fetchNotifications(params)
    
    if (result) {
      total.value = result.count
    }
  } catch (error) {
    console.error('Failed to load notifications:', error)
    ElMessage.error('加载通知失败，请重试')
  } finally {
    loading.value = false
  }
}

// 事件处理方法
function handleTabChange(tabName) {
  currentPage.value = 1
  loadNotifications()
}

function handleFilterChange() {
  currentPage.value = 1
  loadNotifications()
}

function handlePageChange(page) {
  currentPage.value = page
  loadNotifications()
  
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function handleNotificationClick(notification) {
  selectedNotification.value = notification
  showDetailDialog.value = true

  // 自动标记为已读
  if (!notification.is_read) {
    try {
      await notificationsStore.markAsRead(notification.id)
    } catch (error) {
      console.error('Failed to mark as read:', error)
    }
  }
}

async function handleMarkRead(notificationId) {
  try {
    await notificationsStore.markAsRead(notificationId)
    ElMessage.success('已标记为已读')
  } catch (error) {
    ElMessage.error('操作失败，请重试')
  }
}

async function handleMarkAllRead() {
  try {
    await ElMessageBox.confirm(
      '确定要将所有通知标记为已读吗？',
      '确认操作',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    markingAllRead.value = true
    
    const result = await notificationsStore.markAllAsRead()
    ElMessage.success(`成功标记 ${result.updated_count} 条通知为已读`)
    
    // 刷新列表
    await loadNotifications()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败，请重试')
    }
  } finally {
    markingAllRead.value = false
  }
}

function handleGoToLink(link) {
  if (link) {
    router.push(link)
  }
}

// 生命周期
onMounted(async () => {
  // 并行加载未读数量和通知列表
  await Promise.all([
    notificationsStore.fetchUnreadCount(),
    loadNotifications()
  ])
})
</script>

<style scoped lang="scss">
.notification-center {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;

    h2 {
      margin: 0;
      font-size: 24px;
      font-weight: 700;
      color: var(--el-text-color-primary);
    }

    .header-actions {
      display: flex;
      gap: 12px;
      align-items: center;
    }
  }

  .stats-row {
    margin-bottom: 24px;

    .stat-card {
      cursor: pointer;
      transition: transform 0.2s;

      &:hover {
        transform: translateY(-2px);
      }

      &.type-all { border-top: 3px solid #409eff; }
      &.type-system { border-top: 3px solid #409eff; }
      &.type-learning { border-top: 3px solid #e6a23c; }
      &.type-practice { border-top: 3px solid #67c23a; }

      .stat-content {
        display: flex;
        align-items: center;
        gap: 16px;

        .stat-icon {
          width: 56px;
          height: 56px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          background-color: var(--el-fill-color-light);
        }

        .stat-info {
          .stat-count {
            font-size: 28px;
            font-weight: 700;
            color: var(--el-text-color-primary);
            line-height: 1.2;
          }

          .stat-label {
            font-size: 14px;
            color: var(--el-text-color-secondary);
            margin-top: 4px;
          }
        }
      }
    }
  }

  .filter-bar {
    background-color: white;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);

    :deep(.el-tabs__header) {
      margin-bottom: 0;
    }

    .filter-actions {
      display: flex;
      gap: 12px;
      margin-top: 16px;
      justify-content: flex-end;
    }
  }

  .notification-list-container {
    min-height: 400px;

    .loading-state,
    .empty-state {
      padding: 60px 20px;
      text-align: center;
    }

    .notification-list {
      display: flex;
      flex-direction: column;
      gap: 12px;

      .notification-card {
        display: flex;
        gap: 16px;
        padding: 20px;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        cursor: pointer;
        transition: all 0.25s ease;
        border-left: 4px solid transparent;

        &:hover {
          box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
          transform: translateY(-1px);
        }

        &.unread {
          background-color: rgba(var(--el-color-primary-rgb), 0.02);
          border-left-color: var(--el-color-primary);

          .card-title {
            font-weight: 600;
          }
        }

        &.priority-urgent {
          border-left-color: #f56c6c;
        }

        &.priority-high {
          border-left-color: #e6a23c;
        }

        .card-left {
          position: relative;
          flex-shrink: 0;

          .notification-type-badge {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;

            &.type-system { background-color: rgba(64, 158, 255, 0.1); color: #409eff; }
            &.type-learning { background-color: rgba(230, 162, 60, 0.1); color: #e6a23c; }
            &.type-practice { background-color: rgba(103, 194, 58, 0.1); color: #67c23a; }
            &.type-interaction { background-color: rgba(144, 147, 153, 0.1); color: #909399; }
            &.type-announcement { background-color: rgba(245, 108, 108, 0.1); color: #f56c6c; }
          }

          .unread-indicator {
            position: absolute;
            top: -4px;
            right: -4px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background-color: var(--el-color-danger);
            animation: pulse 2s infinite;
          }
        }

        .card-content {
          flex: 1;
          min-width: 0;

          .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;

            .card-title {
              margin: 0;
              font-size: 16px;
              color: var(--el-text-color-primary);
              overflow: hidden;
              text-overflow: ellipsis;
              white-space: nowrap;
              max-width: calc(100% - 80px);
            }
          }

          .card-description {
            margin: 0 0 12px;
            font-size: 14px;
            line-height: 1.6;
            color: var(--el-text-color-regular);
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
          }

          .card-meta {
            display: flex;
            gap: 16px;
            font-size: 13px;
            color: var(--el-text-color-placeholder);

            .meta-time,
            .meta-sender {
              display: flex;
              align-items: center;
              gap: 4px;
            }
          }
        }

        .card-actions {
          flex-shrink: 0;
          display: flex;
          flex-direction: column;
          gap: 8px;
          justify-content: center;
        }
      }
    }

    .pagination-wrapper {
      margin-top: 32px;
      display: flex;
      justify-content: center;
    }
  }

  .notification-detail {
    .detail-header {
      display: flex;
      gap: 16px;
      align-items: flex-start;

      .detail-type {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;

        &.type-system { background-color: rgba(64, 158, 255, 0.1); color: #409eff; }
        &.type-learning { background-color: rgba(230, 162, 60, 0.1); color: #e6a23c; }
        &.type-practice { background-color: rgba(103, 194, 58, 0.1); color: #67c23a; }
      }

      .detail-title-section {
        flex: 1;

        h3 {
          margin: 0 0 8px;
          font-size: 18px;
          color: var(--el-text-color-primary);
        }

        .detail-meta {
          display: flex;
          gap: 12px;
          align-items: center;
          color: var(--el-text-color-secondary);
          font-size: 14px;
        }
      }
    }

    .detail-content {
      padding: 16px 0;
      line-height: 1.8;
      color: var(--el-text-color-regular);
      font-size: 15px;
    }

    .detail-footer {
      display: flex;
      gap: 12px;
      justify-content: flex-end;
      padding-top: 16px;
      border-top: 1px solid var(--el-border-color-lighter);
    }
  }
}

// 动画
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(1.1); }
}

.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
