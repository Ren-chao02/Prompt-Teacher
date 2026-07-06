<template>
  <el-dropdown
    trigger="click"
    placement="bottom-end"
    @visible-change="handleDropdownVisible"
    class="notification-bell"
  >
    <div class="bell-wrapper">
      <!-- 铃铛图标 + 未读数量徽章 -->
      <el-badge :value="unreadCount" :hidden="!hasUnread" :max="99">
        <el-button circle :class="{ 'is-connected': wsConnected }">
          <el-icon :size="20">
            <Bell />
          </el-icon>
        </el-button>
      </el-badge>

      <!-- WebSocket连接状态指示器 -->
      <div 
        v-if="showConnectionStatus"
        class="connection-status"
        :class="{ connected: wsConnected, disconnected: !wsConnected }"
        :title="wsConnected ? '实时推送已连接' : '实时推送未连接'"
      />
    </div>

    <template #dropdown>
      <div class="notification-dropdown">
        <!-- 头部 -->
        <div class="dropdown-header">
          <h3>消息通知</h3>
          <div class="header-actions">
            <el-tag 
              v-if="hasUnread" 
              type="danger" 
              size="small"
              effect="dark"
              round
            >
              {{ unreadCount }} 条未读
            </el-tag>
            <el-button
              v-if="hasUnread"
              link
              type="primary"
              size="small"
              @click.stop="handleMarkAllRead"
              :loading="markingAllRead"
            >
              全部已读
            </el-button>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>

        <!-- 空状态 -->
        <div v-else-if="recentNotifications.length === 0" class="empty-state">
          <el-empty description="暂无通知" :image-size="80" />
        </div>

        <!-- 通知列表（最多显示5条） -->
        <div v-else class="notification-list">
          <div
            v-for="notif in recentNotifications"
            :key="notif.id"
            class="notification-item"
            :class="{ unread: !notif.is_read }"
            @click="handleNotificationClick(notif)"
          >
            <!-- 图标 -->
            <div class="notification-icon" :class="[`type-${notif.notification_type}`, `priority-${notif.priority}`]">
              <el-icon>
                <component :is="getNotificationIcon(notif.notification_type)" />
              </el-icon>
            </div>

            <!-- 内容 -->
            <div class="notification-content">
              <div class="notification-title">{{ notif.title }}</div>
              <div class="notification-meta">
                <span class="time-ago">{{ notif.time_ago || formatTime(notif.created_at) }}</span>
                <el-tag 
                  v-if="!notif.is_read" 
                  type="danger" 
                  size="small" 
                  effect="dark"
                  round
                  class="unread-dot"
                >
                  新
                </el-tag>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部操作 -->
        <div class="dropdown-footer">
          <router-link to="/notifications" class="view-all-link">
            查看全部通知 →
          </router-link>
        </div>
      </div>
    </template>
  </el-dropdown>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationsStore } from '@/stores/notifications'
import { ElMessage } from 'element-plus'
import { Bell, Loading, ChatDotRound, Document, Trophy, Warning, InfoFilled } from '@element-plus/icons-vue'

const router = useRouter()
const notificationsStore = useNotificationsStore()

// 响应式数据
const markingAllRead = ref(false)
const showConnectionStatus = ref(true)

// 计算属性
const unreadCount = computed(() => notificationsStore.unreadCount)
const hasUnread = computed(() => notificationsStore.hasUnread)
const wsConnected = computed(() => notificationsStore.wsConnected)
const loading = computed(() => notificationsStore.loading)
const recentNotifications = computed(() => 
  notificationsStore.notifications.slice(0, 5)
)

// 图标映射
function getNotificationIcon(type) {
  const iconMap = {
    'system': InfoFilled,
    'learning': Document,
    'practice': Trophy,
    'interaction': ChatDotRound,
    'announcement': Warning,
  }
  return iconMap[type] || InfoFilled
}

// 时间格式化
function formatTime(timeStr) {
  if (!timeStr) return ''
  
  const date = new Date(timeStr)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins}分钟前`
  if (diffHours < 24) return `${diffHours}小时前`
  if (diffDays < 7) return `${diffDays}天前`
  
  return date.toLocaleDateString('zh-CN')
}

// 事件处理
async function handleDropdownVisible(visible) {
  if (visible && recentNotifications.value.length === 0) {
    // 下拉时加载最新通知
    await notificationsStore.fetchNotifications({ page_size: 5 })
  }
}

async function handleNotificationClick(notification) {
  // 标记为已读
  if (!notification.is_read) {
    try {
      await notificationsStore.markAsRead(notification.id)
      ElMessage.success('已标记为已读')
    } catch (error) {
      console.error('Failed to mark as read:', error)
    }
  }

  // 如果有链接，跳转
  if (notification.link) {
    router.push(notification.link)
  }
}

async function handleMarkAllRead() {
  markingAllRead.value = true
  
  try {
    const result = await notificationsStore.markAllAsRead()
    ElMessage.success(`成功标记 ${result.updated_count} 条通知为已读`)
  } catch (error) {
    ElMessage.error('操作失败，请重试')
  } finally {
    markingAllRead.value = false
  }
}

// 生命周期
onMounted(() => {
  // 初始化WebSocket连接
  notificationsStore.connectWebSocket()
  
  // 初始获取未读数量
  notificationsStore.fetchUnreadCount()
})

onUnmounted(() => {
  // 组件卸载时断开WebSocket
  notificationsStore.disconnectWebSocket()
})
</script>

<style scoped lang="scss">
.notification-bell {
  .bell-wrapper {
    position: relative;
    display: inline-flex;
    align-items: center;
    
    .el-button {
      border: none;
      
      &.is-connected {
        color: var(--el-color-success);
        
        &:hover {
          background-color: rgba(var(--el-color-success-rgb), 0.1);
        }
      }
    }

    .connection-status {
      position: absolute;
      top: -2px;
      right: -2px;
      width: 10px;
      height: 10px;
      border-radius: 50%;
      border: 2px solid white;

      &.connected {
        background-color: var(--el-color-success);
      }

      &.disconnected {
        background-color: var(--el-color-info-light-5);
      }
    }
  }
}

.notification-dropdown {
  width: 380px;
  max-height: 500px;
  display: flex;
  flex-direction: column;

  .dropdown-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--el-border-color-lighter);
    display: flex;
    justify-content: space-between;
    align-items: center;

    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }

    .header-actions {
      display: flex;
      gap: 8px;
      align-items: center;
    }
  }

  .loading-container {
    padding: 40px;
    text-align: center;
    color: var(--el-text-color-secondary);

    .el-icon {
      margin-right: 8px;
    }
  }

  .empty-state {
    padding: 20px;
  }

  .notification-list {
    overflow-y: auto;
    max-height: 350px;
    padding: 8px 0;

    .notification-item {
      display: flex;
      align-items: flex-start;
      padding: 12px 20px;
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover {
        background-color: var(--el-fill-color-light);
      }

      &.unread {
        background-color: rgba(var(--el-color-danger-rgb), 0.04);

        .notification-title {
          font-weight: 600;
          color: var(--el-text-color-primary);
        }
      }

      .notification-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 12px;
        flex-shrink: 0;
        font-size: 18px;

        &.type-system { background-color: rgba(64, 158, 255, 0.1); color: #409eff; }
        &.type-learning { background-color: rgba(230, 162, 60, 0.1); color: #e6a23c; }
        &.type-practice { background-color: rgba(103, 194, 58, 0.1); color: #67c23a; }
        &.type-interaction { background-color: rgba(144, 147, 153, 0.1); color: #909399; }
        &.type-announcement { background-color: rgba(245, 108, 108, 0.1); color: #f56c6c; }

        &.priority-high,
        &.priority-urgent {
          animation: pulse 2s infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.6; }
        }
      }

      .notification-content {
        flex: 1;
        min-width: 0;

        .notification-title {
          font-size: 14px;
          line-height: 1.4;
          margin-bottom: 4px;
          color: var(--el-text-color-regular);
          overflow: hidden;
          text-overflow: ellipsis;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
        }

        .notification-meta {
          display: flex;
          justify-content: space-between;
          align-items: center;

          .time-ago {
            font-size: 12px;
            color: var(--el-text-color-placeholder);
          }

          .unread-dot {
            transform: scale(0.8);
          }
        }
      }
    }
  }

  .dropdown-footer {
    padding: 12px 20px;
    border-top: 1px solid var(--el-border-color-lighter);
    text-align: center;

    .view-all-link {
      font-size: 14px;
      color: var(--el-color-primary);
      text-decoration: none;
      transition: color 0.2s;

      &:hover {
        color: var(--el-color-primary-light-3);
      }
    }
  }
}
</style>
