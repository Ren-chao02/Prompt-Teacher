<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <div class="logo" @click="$router.push('/dashboard')">
        <el-icon class="logo-icon"><ChatDotRound /></el-icon>
        <h1 v-if="!isCollapse">Prompt Teacher</h1>
        <span v-else>PT</span>
      </div>

      <el-scrollbar>
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :collapse-transition="false"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          router
          :unique-opened="true"
        >
          <template v-for="menu in menuList" :key="menu.path">
            <!-- 有子菜单 -->
            <el-sub-menu
              v-if="menu.children && menu.children.length && hasPermission(menu)"
              :index="menu.path"
            >
              <template #title>
                <el-icon><component :is="menu.icon" /></el-icon>
                <span>{{ menu.title }}</span>
              </template>

              <el-menu-item
                v-for="child in menu.children"
                :key="child.path"
                :index="child.path"
                v-show="hasPermission(child)"
              >
                <el-icon><component :is="child.icon || Document" /></el-icon>
                <template #title>{{ child.title }}</template>
              </el-menu-item>
            </el-sub-menu>

            <!-- 无子菜单 -->
            <el-menu-item
              v-else-if="hasPermission(menu)"
              :index="menu.path"
            >
              <el-icon class="menu-icon"><component :is="menu.icon" /></el-icon>
              <template #title>{{ menu.title }}</template>
            </el-menu-item>
          </template>
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <!-- 主内容区 -->
    <el-container>
      <!-- 头部 -->
      <el-header class="header">
        <div class="header-left">
          <el-icon
            class="collapse-btn"
            @click="toggleCollapse"
          >
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>

          <!-- 动态面包屑 -->
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item
              v-for="(item, index) in breadcrumbs"
              :key="item.path"
              :to="index < breadcrumbs.length - 1 ? { path: item.path } : undefined"
            >
              {{ item.meta?.title || item.name }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- 欢迎语（仅展开时显示） -->
          <div v-if="!isCollapse" class="greeting">
            <el-icon class="greeting-icon"><Sunny /></el-icon>
            <span class="greeting-text">{{ greetingText }}</span>
          </div>

          <!-- 全屏按钮 -->
          <el-tooltip content="全屏切换" placement="bottom">
            <el-icon class="action-btn" @click="toggleFullScreen">
              <FullScreen />
            </el-icon>
          </el-tooltip>

          <!-- 通知铃铛 -->
          <NotificationBell />

          <!-- 用户下拉菜单 -->
          <el-dropdown trigger="click" @command="handleCommand">
            <span class="user-info">
              <el-avatar
                :size="32"
                :src="authStore.user?.avatar || undefined"
                class="user-avatar"
              >
                {{ (authStore.user?.real_name || authStore.user?.username || 'U').charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="username">{{ authStore.user?.real_name || authStore.user?.username }}</span>
              <el-tag size="small" :type="getRoleTagType(authStore.role)" class="role-tag">
                {{ getRoleLabel(authStore.role) }}
              </el-tag>
              <el-icon class="arrow-icon"><ArrowDown /></el-icon>
            </span>

            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主内容 -->
      <el-main class="main">
        <!-- 页面标题（可选） -->
        <div v-if="showPageTitle" class="page-header">
          <h2>{{ pageTitle }}</h2>
          <p v-if="pageDescription">{{ pageDescription }}</p>
        </div>

        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth'
import {
  ChatDotRound,
  Odometer,
  Monitor,
  Reading,
  Aim,
  DataAnalysis,
  UserFilled,
  User,
  Fold,
  Expand,
  ArrowDown,
  FullScreen,
  SwitchButton,
  Document,
  EditPen,
  Grid,
  List as ListIcon,
  Tickets,
  TrendCharts,
  Histogram,
  House,
  Sunny
} from '@element-plus/icons-vue'
import NotificationBell from '@/components/NotificationBell.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isCollapse = ref(false)

const activeMenu = computed(() => route.path)

const breadcrumbs = computed(() => {
  return route.matched.filter(item => item.meta && item.meta.title)
})

const pageTitle = computed(() => {
  return route.meta?.title || ''
})

const pageDescription = computed(() => {
  return route.meta?.description || ''
})

const showPageTitle = computed(() => {
  return !!route.meta?.title
})

const isAdmin = computed(() => authStore.isAdmin)
const isAdminOrTeacher = computed(() => authStore.isAdminOrTeacher)
// 角色标识（用于日志/调试）
const currentRole = computed(() => authStore.role)

// 欢迎语（按时段+角色）
const greetingText = computed(() => {
  const hour = new Date().getHours()
  const username = authStore.user?.real_name || authStore.user?.username || '同学'
  let timeGreeting = '你好'
  if (hour < 6) timeGreeting = '夜深了，注意休息'
  else if (hour < 11) timeGreeting = '早上好'
  else if (hour < 14) timeGreeting = '中午好'
  else if (hour < 18) timeGreeting = '下午好'
  else timeGreeting = '晚上好'

  const roleGreeting = {
    admin: '管理员',
    teacher: '老师',
    student: '同学'
  }[authStore.role] || ''

  return `${timeGreeting}，${username}${roleGreeting}`
})

const menuList = ref([
  {
    path: '/dashboard',
    title: '仪表盘',
    icon: Odometer,
    roles: ['admin', 'teacher', 'student']
  },
  {
    path: '/teacher/workspace',
    title: '我的工作台',
    icon: Monitor,
    roles: ['admin', 'teacher']
  },
  {
    path: '/learning',
    title: '学习中心',
    icon: Reading,
    roles: ['admin', 'teacher', 'student'],
    children: [
      {
        path: '/learning/list',
        title: '内容列表',
        icon: Document,
        roles: ['admin', 'teacher', 'student']
      },
      {
        path: '/learning/my',
        title: '我的内容',
        icon: EditPen,
        roles: ['admin', 'teacher']
      },
      {
        path: '/learning/create',
        title: '创建内容',
        icon: EditPen,
        roles: ['admin', 'teacher']
      }
    ]
  },
  {
    path: '/practice',
    title: '练习系统',
    icon: Aim,
    roles: ['admin', 'teacher', 'student'],
    children: [
      {
        path: '/practice/scenarios',
        title: '场景管理',
        icon: Grid,
        roles: ['admin', 'teacher']
      },
      {
        path: '/practice/topics',
        title: '主题管理',
        icon: ListIcon,
        roles: ['admin', 'teacher']
      },
      {
        path: '/practice/records',
        title: '练习记录',
        icon: Tickets,
        roles: ['admin', 'teacher', 'student']
      }
    ]
  },
  {
    path: '/analytics',
    title: '数据分析',
    icon: DataAnalysis,
    roles: ['admin', 'teacher', 'student'],
    children: [
      {
        path: '/analytics/overview',
        title: '数据概览',
        icon: Odometer,
        roles: ['admin', 'teacher', 'student']
      },
      {
        path: '/analytics/learning',
        title: '学习进度',
        icon: TrendCharts,
        roles: ['admin', 'teacher', 'student']
      },
      {
        path: '/analytics/practice',
        title: '练习统计',
        icon: Histogram,
        roles: ['admin', 'teacher', 'student']
      }
    ]
  },
  {
    path: '/users/list',
    title: '用户管理',
    icon: UserFilled,
    roles: ['admin']
  },
  {
    path: '/profile',
    title: '个人中心',
    icon: House,
    roles: ['admin', 'teacher', 'student']
  }
])

function hasPermission(menu) {
  if (!menu.roles) return true
  
  const userRole = authStore.role
  return menu.roles.includes(userRole)
}

function toggleCollapse() {
  isCollapse.value = !isCollapse.value
  localStorage.setItem('sidebarCollapsed', isCollapse.value)
}

function toggleFullScreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

async function handleCommand(command) {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'logout':
      await handleLogout()
      break
  }
}

async function handleLogout() {
  await authStore.logout()
  window.location.href = '/admin/login/'
}

function getRoleTagType(role) {
  const map = { admin: 'danger', teacher: 'warning', student: '' }
  return map[role] || 'info'
}

function getRoleLabel(role) {
  const map = { admin: '管理员', teacher: '教师', student: '学生' }
  return map[role] || role
}

watch(
  () => route.path,
  () => {
    document.title = `${pageTitle.value} - Prompt Teacher 管理系统`
  },
  { immediate: true }
)

onMounted(() => {
  const collapsed = localStorage.getItem('sidebarCollapsed')
  if (collapsed === 'true') {
    isCollapse.value = true
  }
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.aside {
  background-color: #304156;
  transition: width 0.3s;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.3s;
  flex-shrink: 0;
  padding: 0 16px;
  white-space: nowrap;
  overflow: visible;
}

.logo-icon {
  font-size: 24px;
  color: #409EFF;
  flex-shrink: 0;
}

.logo h1 {
  margin: 0;
  font-size: 18px;
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 180px;
}

.logo:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.el-scrollbar {
  flex: 1;
  overflow: hidden;
}

.el-menu {
  border-right: none;
}

/* 菜单图标样式 - 关键：必须显式设置 color，避免继承或被覆盖 */
.menu-icon,
.el-menu-item .el-icon,
.el-sub-menu__title .el-icon,
.el-menu--collapse .el-menu-item .el-icon,
.el-menu--collapse .el-sub-menu__title .el-icon {
  width: 24px !important;
  height: 24px !important;
  font-size: 20px !important;
  margin-right: 8px !important;
  vertical-align: middle !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  /* 显式设置颜色，确保与背景形成对比 */
  color: #ffffff !important;
  fill: #ffffff !important;
}

/* 菜单项悬停时图标颜色 */
.el-menu-item:hover .el-icon,
.el-sub-menu__title:hover .el-icon {
  color: #409EFF !important;
  fill: #409EFF !important;
}

/* 菜单项激活时图标颜色 */
.el-menu-item.is-active .el-icon,
.el-sub-menu__title.is-active .el-icon {
  color: #409EFF !important;
  fill: #409EFF !important;
}

/* 折叠状态下的菜单样式 */
.el-menu--collapse .el-menu-item,
.el-menu--collapse .el-sub-menu__title {
  padding: 0 !important;
  text-align: center !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.el-menu--collapse .el-menu-item .el-icon,
.el-menu--collapse .el-sub-menu__title .el-icon {
  margin: 0 !important;
  font-size: 20px !important;
}

/* 修复菜单项文字显示 */
.el-menu-item,
.el-sub-menu__title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.el-sub-menu .el-menu-item {
  padding-left: 50px !important;
  min-width: auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 1px 2px rgba(0, 21, 41, 0.04);
  background: #ffffff;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.breadcrumb {
  font-size: 14px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #6B7280;
  padding: 6px;
  border-radius: 6px;
}

.collapse-btn:hover {
  background-color: #F3F4F6;
  color: #2563EB;
  transform: none;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 欢迎语 */
.greeting {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: linear-gradient(135deg, #DBEAFE 0%, #EFF6FF 100%);
  border-radius: 999px;
  font-size: 13px;
  color: #1E40AF;
  font-weight: 500;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.greeting:hover {
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.15);
}

.greeting-icon {
  font-size: 14px;
  color: #F59E0B;
}

.greeting-text {
  background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.action-btn {
  font-size: 18px;
  cursor: pointer;
  color: #6B7280;
  padding: 6px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background-color: #F3F4F6;
  color: #2563EB;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #111827;
  padding: 4px 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.user-info:hover {
  background-color: #F3F4F6;
}

.user-avatar {
  border: 2px solid #ffffff;
  box-shadow: 0 0 0 1px #E5E7EB;
  background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%);
  color: #ffffff;
  font-weight: 600;
}

.username {
  font-size: 14px;
  font-weight: 500;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.role-tag {
  margin-left: 0;
  border: none;
  font-weight: 500;
}

.arrow-icon {
  font-size: 12px;
  color: #9CA3AF;
  transition: transform 0.2s;
}

.user-info:hover .arrow-icon {
  transform: translateY(1px);
}

.main {
  background-color: #F9FAFB;
  padding: 20px;
  overflow-y: auto;
}

.page-header {
  margin-bottom: 20px;
  padding: 16px 24px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.06);
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.page-header p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

/* 页面过渡动画 */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
