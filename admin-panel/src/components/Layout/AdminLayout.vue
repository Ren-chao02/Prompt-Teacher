<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <div class="logo" @click="$router.push('/dashboard')">
        <h1 v-if="!isCollapse">Prompt Teacher</h1>
        <span v-else>PT</span>
      </div>

      <el-scrollbar>
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
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
                <el-icon><component :is="child.icon || 'Document'" /></el-icon>
                <template #title>{{ child.title }}</template>
              </el-menu-item>
            </el-sub-menu>

            <!-- 无子菜单 -->
            <el-menu-item
              v-else-if="hasPermission(menu)"
              :index="menu.path"
            >
              <el-icon><component :is="menu.icon" /></el-icon>
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
          <el-breadcrumb separator="/">
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
          <!-- 全屏按钮 -->
          <el-tooltip content="全屏切换" placement="bottom">
            <el-icon class="action-btn" @click="toggleFullScreen">
              <FullScreen />
            </el-icon>
          </el-tooltip>

          <!-- 用户下拉菜单 -->
          <el-dropdown trigger="click" @command="handleCommand">
            <span class="user-info">
              <el-avatar 
                :size="32" 
                :src="authStore.user?.avatar || undefined"
              >
                {{ authStore.user?.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <span class="username">{{ authStore.user?.username }}</span>
              <el-tag size="small" :type="getRoleTagType(authStore.role)" style="margin-left: 8px">
                {{ getRoleLabel(authStore.role) }}
              </el-tag>
              <el-icon><ArrowDown /></el-icon>
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
  Odometer,
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
  Document
} from '@element-plus/icons-vue'

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

const menuList = ref([
  {
    path: '/dashboard',
    title: '仪表盘',
    icon: 'Odometer',
    roles: ['admin', 'teacher', 'student']
  },
  {
    path: '/learning',
    title: '学习管理',
    icon: 'Reading',
    roles: ['admin', 'teacher', 'student'],
    children: [
      {
        path: '/learning/list',
        title: '内容列表',
        icon: 'Document',
        roles: ['admin', 'teacher', 'student']
      },
      {
        path: '/learning/create',
        title: '创建内容',
        icon: 'EditPen',
        roles: ['admin', 'teacher']
      },
      {
        path: '/learning/detail/:id',
        title: '内容详情',
        icon: 'View',
        roles: ['admin', 'teacher', 'student'],
        hidden: true
      }
    ]
  },
  {
    path: '/practice',
    title: '练习系统',
    icon: 'Aim',
    roles: ['admin', 'teacher'],
    children: [
      {
        path: '/practice/scenarios',
        title: '场景管理',
        icon: 'Grid',
        roles: ['admin', 'teacher']
      },
      {
        path: '/practice/topics',
        title: '主题管理',
        icon: 'List',
        roles: ['admin', 'teacher']
      },
      {
        path: '/practice/records',
        title: '练习记录',
        icon: 'Tickets',
        roles: ['admin', 'teacher']
      }
    ]
  },
  {
    path: '/statistics',
    title: '数据分析',
    icon: 'DataAnalysis',
    roles: ['admin']
  },
  {
    path: '/users/list',
    title: '用户管理',
    icon: 'UserFilled',
    roles: ['admin']
  },
  {
    path: '/profile',
    title: '个人中心',
    icon: 'User',
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
  router.push('/admin/login')
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
  color: #fff;
  font-size: 20px;
  font-weight: bold;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.3s;
  flex-shrink: 0;
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

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  background: #fff;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  transition: transform 0.3s;
  color: #606266;
}

.collapse-btn:hover {
  transform: scale(1.1);
  color: #409EFF;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.action-btn {
  font-size: 18px;
  cursor: pointer;
  color: #606266;
  transition: color 0.3s;
}

.action-btn:hover {
  color: #409EFF;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #333;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  font-size: 14px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.main {
  background-color: #f0f2f5;
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
