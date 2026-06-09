import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/components/Layout/AdminLayout.vue'),
    meta: { requiresAuth: true },
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: {
          title: '仪表盘',
          icon: 'Odometer',
          roles: ['admin', 'teacher', 'student']
        }
      },
      {
        path: 'teacher/workspace',
        name: 'TeacherWorkspace',
        component: () => import('@/views/teacher/Workspace.vue'),
        meta: {
          title: '我的工作台',
          icon: 'Monitor',
          roles: ['admin', 'teacher']
        }
      },
      {
        path: 'teacher/student/:id',
        name: 'TeacherStudentDetail',
        component: () => import('@/views/teacher/StudentDetail.vue'),
        meta: {
          title: '学生详情',
          roles: ['admin', 'teacher']
        }
      },
      {
        path: 'users/list',
        name: 'UserList',
        component: () => import('@/views/user/list.vue'),
        meta: {
          title: '用户管理',
          icon: 'UserFilled',
          roles: ['admin']
        }
      },
      {
        path: 'users/class',
        name: 'ClassManage',
        component: () => import('@/views/user/class/index.vue'),
        meta: {
          title: '班级管理',
          icon: 'School',
          roles: ['admin']
        }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/user/profile.vue'),
        meta: {
          title: '个人中心',
          icon: 'User',
          roles: ['admin', 'teacher', 'student']
        }
      },
      {
        path: 'learning/list',
        name: 'LearningList',
        component: () => import('@/views/learning/list.vue'),
        meta: {
          title: '学习内容列表',
          icon: 'Reading',
          roles: ['admin', 'teacher', 'student']
        }
      },
      {
        path: 'learning/create',
        name: 'LearningCreate',
        component: () => import('@/views/learning/edit.vue'),
        meta: {
          title: '创建学习内容',
          icon: 'EditPen',
          roles: ['admin', 'teacher']
        }
      },
      {
        path: 'learning/edit/:id',
        name: 'LearningEdit',
        component: () => import('@/views/learning/edit.vue'),
        meta: {
          title: '编辑学习内容',
          icon: 'EditPen',
          roles: ['admin', 'teacher']
        }
      },
      {
        path: 'learning/detail/:id',
        name: 'LearningDetail',
        component: () => import('@/views/learning/detail.vue'),
        meta: {
          title: '内容详情',
          icon: 'Document',
          roles: ['admin', 'teacher', 'student']
        }
      },
      {
        path: 'learning/my',
        name: 'MyMaterials',
        component: () => import('@/views/learning/my-materials.vue'),
        meta: {
          title: '我的内容',
          icon: 'FolderOpened',
          roles: ['admin', 'teacher']
        }
      },
      {
        path: 'practice/scenarios',
        name: 'PracticeScenarios',
        component: () => import('@/views/practice/scenarios.vue'),
        meta: {
          title: '练习场景',
          icon: 'Aim',
          roles: ['admin', 'teacher']
        }
      },
      {
        path: 'practice/topics',
        name: 'PracticeTopics',
        component: () => import('@/views/practice/topics.vue'),
        meta: {
          title: '主题管理',
          icon: 'List',
          roles: ['admin', 'teacher']
        }
      },
      {
        path: 'practice/records',
        name: 'PracticeRecords',
        component: () => import('@/views/practice/records.vue'),
        meta: {
          title: '练习记录',
          icon: 'DocumentChecked',
          roles: ['admin', 'student']
        }
      },
      {
        path: 'analytics/overview',
        name: 'AnalyticsOverview',
        component: () => import('@/views/analytics/Overview.vue'),
        meta: {
          title: '数据分析概览',
          icon: 'DataAnalysis',
          roles: ['admin', 'teacher', 'student']
        }
      },
      {
        path: 'analytics/learning',
        name: 'LearningProgress',
        component: () => import('@/views/analytics/LearningProgress.vue'),
        meta: {
          title: '学习进度分析',
          icon: 'TrendCharts',
          roles: ['admin', 'teacher', 'student']
        }
      },
      {
        path: 'analytics/practice',
        name: 'PracticeStatistics',
        component: () => import('@/views/analytics/PracticeStatistics.vue'),
        meta: {
          title: '练习成绩统计',
          icon: 'Histogram',
          roles: ['admin', 'teacher', 'student']
        }
      },
      {
        path: 'notifications',
        name: 'NotificationCenter',
        component: () => import('@/views/NotificationCenter.vue'),
        meta: {
          title: '消息通知',
          icon: 'Bell',
          roles: ['admin', 'teacher', 'student']
        }
      }
    ]
  },
  {
    path: '/403',
    name: 'Forbidden',
    component: () => import('@/views/error/403.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue')
  }
]

const router = createRouter({
  history: createWebHistory('/admin/'),
  routes
})

let isInitialized = false

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  if (!isInitialized && authStore.token && !authStore.user) {
    try {
      await authStore.fetchUserInfo()
    } catch (error) {
      console.error('路由守卫：恢复用户信息失败:', error)
      authStore.logout()

      if (to.path !== '/login') {
        next({ path: '/login', query: { redirect: to.fullPath } })
        return
      }
    }

    isInitialized = true
  }

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  if (to.meta.roles && to.meta.roles.length > 0) {
    if (!authStore.role || !to.meta.roles.includes(authStore.role)) {
      next('/403')
      return
    }
  }

  // 教师登录后优先进入工作台
  if ((to.path === '/' || to.path === '/dashboard') && authStore.role === 'teacher') {
    next('/teacher/workspace')
    return
  }

  next()
})

export default router