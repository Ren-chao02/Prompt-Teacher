# Prompt Teacher 后台管理系统 - 设计规范文档

**项目名称**: Prompt Teacher Admin Panel  
**版本**: v1.0  
**日期**: 2026-05-30  
**状态**: ✅ 已审核通过  
**作者**: AI Assistant (Brainstorming Skill)  

---

## 📋 目录

1. [项目概述](#1-项目概述)
2. [技术选型](#2-技术选型)
3. [系统架构](#3-系统架构)
4. [数据模型设计](#4-数据模型设计)
5. [权限体系](#5-权限体系)
6. [功能模块详细设计](#6-功能模块详细设计)
7. [API 设计规范](#7-api-设计规范)
8. [前端架构](#8-前端架构)
9. [安全性设计](#9-安全性设计)
10. [部署方案](#10-部署方案)

---

## 1. 项目概述

### 1.1 项目背景

**Prompt Teacher** 是一个提示词工程教学平台，目前拥有：
- 完整的前台学习系统（学习资料 + 练习场景）
- Django 6.0.4 后端 + Bootstrap 5 前端
- SQLite/PostgreSQL 双数据库支持
- 三级用户角色体系（管理员 / 教师 / 学生）

### 1.2 项目目标

构建一个**现代化、高性能、易维护**的后台管理系统，实现：

✅ **内容管理**: 学习资料、练习场景的 CRUD 操作  
✅ **数据洞察**: 用户行为、学习效果的可视化分析  
✅ **用户管理**: 多角色权限控制、师生关系管理  
✅ **效率提升**: 批量操作、数据导出、自动化流程  

### 1.3 目标用户

| 角色 | 典型用户 | 核心需求 |
|------|---------|---------|
| **超级管理员 (admin)** | 平台负责人 | 全局管控、系统配置 |
| **教师 (teacher)** | 课程编辑者 | 内容维护、学生管理 |
| **学生 (student)** | 普通学习者 | 个人数据查看、学习追踪 |

---

## 2. 技术选型

### 2.1 整体架构: 前后端分离 (SPA)

**选择理由**: 
- 解耦前后端，支持独立开发与部署
- Vue 3 SPA 提供流畅的用户体验
- 便于未来扩展移动端 App
- 符合现代 Web 开发最佳实践

### 2.2 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Django** | 6.0.4 | Web 框架 |
| **Django REST Framework** | 3.15.x | REST API 开发 |
| **Simple JWT** | 5.x | JWT 认证 |
| **django-cors-headers** | 4.x | 跨域处理 |
| **PostgreSQL** | 15+ | 生产数据库 |
| **Redis** | 7.x | 缓存 & 会话存储 |

### 2.3 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **Vue 3** | 3.4+ | 前端框架 (Composition API) |
| **Vite** | 5.x | 构建工具 |
| **Element Plus** | 2.x | UI 组件库 |
| **Vue Router** | 4.x | 路由管理 |
| **Pinia** | 2.x | 状态管理 |
| **Axios** | 1.x | HTTP 客户端 |
| **ECharts** | 5.x | 数据可视化 |
| **md-editor-v3** | 4.x | Markdown 编辑器 |

---

## 3. 系统架构

### 3.1 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     用户浏览器 (Vue 3)                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    Admin Panel                        │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────┐  │  │
│  │  │ Router  │ │  Pinia  │ │ Axios   │ │ Element+ │  │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └───────────┘  │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐               │  │
│  │  │ ECharts │ │ MD Edit │ │ Utils   │               │  │
│  │  └─────────┘ └─────────┘ └─────────┘               │  │
│  └───────────────────────┬───────────────────────────────┘  │
└──────────────────────────┼─────────────────────────────────┘
                           │ HTTP/JSON (REST API)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Django Backend (API)                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Django REST Framework                     │  │
│  │  ┌──────────┐ ┌──────────┐ ┌────────────────────┐    │  │
│  │  │ Auth     │ │ Permissions │ │ ViewSets          │    │  │
│  │  │ (JWT)    │ │ (RBAC)   │ │ (CRUD)            │    │  │
│  │  └──────────┘ └──────────┘ └────────────────────┘    │  │
│  ├───────────────────────────────────────────────────────┤  │
│  │  应用模块                                                │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐  │  │
│  │  │ users    │ │ learning │ │ practice │ │ core    │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └─────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │PostgreSQL│ │  Redis   │ │ Media    │
        │ (主数据库)│ │ (缓存)   │ │ (文件)   │
        └──────────┘ └──────────┘ └──────────┘
```

### 3.2 项目目录结构

#### **后端目录结构**
```
Prompt Teacher/
├── backend/                          # Django API 服务
│   ├── prompt_teaching/              # 项目配置
│   │   ├── __init__.py
│   │   ├── settings.py               # 配置 (新增 DRF, JWT, CORS)
│   │   ├── urls.py                   # 主路由
│   │   └── wsgi.py
│   │
│   ├── users/                        # 用户应用 (扩展)
│   │   ├── __init__.py
│   │   ├── models.py                 # UserProfile 模型
│   │   ├── admin.py                  # Django Admin 注册
│   │   ├── serializers.py            # 用户序列化器
│   │   ├── permissions.py            # 权限类 (IsAdmin, IsTeacher, etc.)
│   │   ├── middleware.py             # 数据权限中间件
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── urls.py               # 用户 API 路由
│   │   │   └── views.py               # 用户视图集
│   │   └── tests.py
│   │
│   ├── learning/                     # 学习应用
│   │   ├── models.py                 # LearningMaterial (已有)
│   │   ├── api/
│   │   │   ├── urls.py
│   │   │   ├── views.py              # LearningMaterialViewSet
│   │   │   └── serializers.py
│   │   └── ...
│   │
│   ├── practice/                    # 练习应用
│   │   ├── models.py                 # PracticeScenario, Topic, Record
│   │   ├── api/
│   │   │   ├── urls.py
│   │   │   ├── views.py
│   │   │   └── serializers.py
│   │   └── ...
│   │
│   └── core/                         # 核心应用
│       ├── api/
│       │   ├── urls.py
│       │   ├── views.py              # Statistics Views
│       │   └── serializers.py
│       └── ...
│
├── requirements.txt                  # 新增依赖
└── manage.py
```

#### **前端目录结构**
```
admin-panel/                           # Vue 3 独立项目
├── public/
│   └── favicon.ico
│
├── src/
│   ├── api/                          # API 封装层
│   │   ├── request.js                # Axios 实例、拦截器
│   │   ├── auth.js                   # 认证相关 API
│   │   ├── user.js                   # 用户管理 API
│   │   ├── learning.js               # 学习内容 API
│   │   ├── practice.js               # 练习系统 API
│   │   └── statistics.js             # 统计数据 API
│   │
│   ├── assets/                       # 静态资源
│   │   ├── images/
│   │   └── styles/
│   │       ├── variables.css         # CSS 变量 (复用前台)
│   │       └── element-variables.scss # Element Plus 定制
│   │
│   ├── components/                   # 全局组件
│   │   ├── Layout/
│   │   │   ├── AdminLayout.vue      # 主布局 (侧边栏 + 顶栏 + 内容区)
│   │   │   ├── Sidebar.vue          # 侧边导航菜单
│   │   │   ├── Navbar.vue           # 顶部导航栏
│   │   │   └── Breadcrumb.vue       # 面包屑导航
│   │   │
│   │   └── Common/
│   │       ├── StatCard.vue         # 统计卡片
│   │       ├── SearchBar.vue        # 搜索栏
│   │       ├── Pagination.vue       # 分页器
│   │       ├── ConfirmDialog.vue    # 确认对话框
│   │       └── ImageUpload.vue      # 图片上传
│   │
│   ├── views/                        # 页面视图
│   │   ├── login/                   # 登录模块
│   │   │   └── index.vue
│   │   │
│   │   ├── dashboard/               # 仪表盘
│   │   │   └── index.vue
│   │   │
│   │   ├── learning/                # 学习管理
│   │   │   ├── list.vue             # 内容列表
│   │   │   ├── edit.vue             # 创建/编辑
│   │   │   └── detail.vue           # 详情页
│   │   │
│   │   ├── practice/                # 练习管理
│   │   │   ├── scenarios.vue        # 场景管理
│   │   │   ├── topics.vue          # 主题管理
│   │   │   ├── records.vue         # 练习记录
│   │   │   └── my-records.vue      # 我的练习 (学生)
│   │   │
│   │   ├── statistics/              # 数据统计
│   │   │   ├── overview.vue         # 总览
│   │   │   ├── users.vue           # 用户分析
│   │   │   ├── content.vue         # 内容分析
│   │   │   └── practice.vue        # 练习分析
│   │   │
│   │   ├── user/                    # 用户管理
│   │   │   ├── list.vue            # 用户列表
│   │   │   ├── create.vue          # 创建用户
│   │   │   ├── profile.vue         # 个人中心
│   │   │   └── students.vue        # 我的学生 (教师)
│   │   │
│   │   └── error/                   # 错误页面
│   │       ├── 403.vue
│   │       └── 404.vue
│   │
│   ├── router/                      # 路由配置
│   │   ├── index.js                 # 路由定义
│   │   └── permission.js            # 路由守卫
│   │
│   ├── store/                       # Pinia 状态管理
│   │   ├── modules/
│   │   │   ├── auth.js              # 认证状态 (token, user, role)
│   │   │   ├── app.js               # 应用状态 (sidebar, theme)
│   │   │   └── user.js              # 用户相关状态
│   │   └── index.js
│   │
│   ├── config/                      # 配置文件
│   │   ├── menu.js                  # 动态菜单配置
│   │   ├── constants.js             # 常量定义
│   │   └── settings.js              # 环境配置
│   │
│   ├── utils/                       # 工具函数
│   │   ├── auth.js                  # Token 管理
│   │   ├── format.js                # 格式化函数
│   │   ├── validate.js              # 表单验证
│   │   └── permission.js            # 权限工具
│   │
│   ├── permission.js                # 全局权限指令
│   ├── App.vue
│   └── main.js
│
├── .env.development                 # 开发环境变量
├── .env.production                  # 生产环境变量
├── vite.config.js                   # Vite 配置
├── package.json
└── index.html
```

---

## 4. 数据模型设计

### 4.1 UserProfile (扩展用户模型)

```python
# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class UserProfile(AbstractUser):
    """增强用户模型 - 支持教育场景"""
    
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('teacher', '教师'),
        ('student', '学生'),
    ]
    
    # ====== 基础字段 ======
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name='角色',
        db_index=True
    )
    
    phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='手机号'
    )
    
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/',
        null=True,
        blank=True,
        verbose_name='头像'
    )
    
    # ====== 学生专属字段 ======
    student_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        verbose_name='学号',
        help_text='仅学生角色需要填写，全局唯一'
    )
    
    semester = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='学期',
        help_text='格式: 2024-2025-1'
    )
    
    major = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='专业'
    )
    
    # ====== 关联字段 ======
    teacher = models.ForeignKey(
        'self',  # 自引用外键
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        limit_choices_to={'role': 'teacher'},
        verbose_name='指导教师',
        help_text='仅学生角色需要选择'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    class Meta:
        verbose_name = '用户档案'
        verbose_name_plural = '用户档案'
        ordering = ['-date_joined']
    
    def __str__(self):
        if self.role == 'student' and self.student_id:
            return f'{self.student_id} - {self.get_full_name()}'
        return self.get_full_name() or self.username
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_teacher(self):
        return self.role in ['admin', 'teacher']
```

### 4.2 关系说明

```
UserProfile (自引用关系)
├── admin (管理员)
│   └── 可查看所有用户和数据
│
├── teacher (教师)
│   ├── 通过 FK 'students' 关联多个 Student
│   └── 只能查看自己名下学生的数据
│
└── student (学生)
    ├── 通过 FK 'teacher' 关联一个 Teacher
    └── 只能查看自己的个人数据
```

---

## 5. 权限体系

### 5.1 角色定义

| 角色 | 标识符 | 描述 | 数据范围 |
|------|--------|------|---------|
| **超级管理员** | `admin` | 平台负责人 | 全部数据 |
| **教师** | `teacher` | 课程编辑者 | 自己 + 名下学生 |
| **学生** | `student` | 普通学习者 | 仅个人 |

### 5.2 权限矩阵

| 功能模块 | admin | teacher | student |
|----------|-------|---------|---------|
| **📊 Dashboard** | ✅ | ✅ | ✅ (个人化) |
| **📚 学习内容 CRUD** | ✅ | ✅ | ❌ |
| **🎯 场景/主题管理** | ✅ | ✅ | ❌ |
| **📈 全局数据统计** | ✅ | ✅ (所教学生) | ✅ (个人) |
| **👥 用户列表** | ✅ 全部 | ✅ 学生列表 | ❌ |
| **👤 创建/编辑用户** | ✅ | ✅ 仅学生账号 | ❌ |
| **⚙️ 系统设置** | ✅ | ❌ | ❌ |
| **📋 个人中心** | ✅ | ✅ | ✅ |
| **📝 练习记录查看** | ✅ 全部 | ✅ 学生记录 | ✅ 仅自己的 |

### 5.3 技术实现

#### **后端: DRF 权限类**

```python
# users/permissions.py
from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """仅管理员可访问"""
    message = '只有管理员才能执行此操作'
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated 
            and getattr(request.user, 'role', None) == 'admin'
        )

class IsTeacher(permissions.BasePermission):
    """教师及以上角色可访问"""
    message = '只有教师或管理员才能执行此操作'
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated 
            and getattr(request.user, 'role', None) in ['admin', 'teacher']
        )

class IsOwnerOrReadOnly(permissions.BasePermission):
    """所有认证用户可读，仅所有者可写"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 检查对象是否属于当前用户
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return False
```

#### **前端: 路由守卫 + 动态菜单**

```javascript
// src/router/index.js
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
      // ... 其他路由
    ]
  }
]

// 全局前置守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 未登录且需要认证 → 跳转登录
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }
  
  // 已登录但无权限 → 跳转 403
  if (to.meta.roles && !to.meta.roles.includes(userStore.role)) {
    next('/403')
    return
  }
  
  next()
})
```

---

## 6. 功能模块详细设计

### 6.1 Dashboard (仪表盘)

**路由**: `/dashboard`  
**权限**: 所有角色  
**核心功能**: 数据概览、趋势分析、快捷入口

#### **页面元素**
1. **统计卡片** (4个)
   - 总用户数 / 本月新增
   - 学习资料数 / 今日发布
   - 练习完成率 / 平均分
   - 今日活跃度

2. **图表区域** (2-3个)
   - 学习趋势折线图 (近30天)
   - 练习分布饼图 (按场景分类)
   - 用户活跃度柱状图 (按周)

3. **快捷入口**
   - 待处理事项列表
   - 热门内容 TOP 5
   - 最近活动动态

#### **技术要点**
- 使用 ECharts 5 渲染图表
- 数据通过 API 实时获取 (缓存 5 分钟)
- 支持时间范围切换 (日/周/月)

---

### 6.2 学习内容管理

**路由前缀**: `/learning/*`  
**权限**: admin, teacher

#### **子功能**

##### **6.2.1 内容列表 (`/learning/list`)**
- **搜索**: 标题、分类、状态筛选
- **排序**: 创建时间、阅读量、排序权重
- **批量操作**: 删除、修改分类、批量发布/下架
- **表格列**: 标题、分类(Badge)、排序、阅读量、状态、操作

##### **6.2.2 内容编辑 (`/learning/edit/:id?`)**
- **基本信息表单**: 标题、分类(Select)、排序(Number)、状态(Switch)
- **Markdown 编辑器**: md-editor-v3，支持实时预览
- **保存选项**: 草稿 / 发布
- **自动保存**: 每 30 秒自动保存草稿

##### **6.2.3 内容详情 (`/learning/detail/:id`)**
- **只读模式**: Markdown 渲染后的 HTML
- **元信息**: 作者、创建时间、最后修改、阅读量
- **关联操作**: 编辑、删除、复制

---

### 6.3 练习系统管理

**路由前缀**: `/practice/*`  
**权限**: admin, teacher (部分学生可见)

#### **子功能**

##### **6.3.1 场景管理 (`/practice/scenarios`)**
- **卡片式布局**: 图标 + 标题 + 描述 + 难度标签
- **CRUD 操作**: 创建、编辑、删除、启用/禁用
- **拖拽排序**: 调整场景显示顺序

##### **6.3.2 主题管理 (`/practice/topics/:scenario_id`)**
- **嵌套表格**: 属于某场景的所有主题
- **字段编辑**: 编号、标题、描述、示例提示词
- **评估标准**: JSON Editor (可视化配置评分规则)

##### **6.3.3 练习记录 (`/practice/records`)**
- **高级筛选**: 时间范围、用户、场景、分数区间
- **数据表格**: 用户、场景、得分(颜色标识)、用时、操作
- **详情弹窗**: 显示完整的用户输入、AI 回复、评分明细
- **导出功能**: Excel / PDF 格式

##### **6.3.4 我的练习 (`/practice/my-records`) [学生专用]
- **历史列表**: 我的练习记录
- **成绩统计**: 平均分、最高分、进步曲线
- **错题本**: 得分 < 70 的主题汇总

---

### 6.4 数据统计分析

**路由前缀**: `/statistics/*`  
**权限**: admin (全部), teacher (所教学生), student (个人)

#### **子模块**

##### **6.4.1 总览面板 (`/statistics/overview`)**
- 用户增长趋势
- 内容热度排行
- 练习通过率
- 平台健康指标

##### **6.4.2 用户分析 (`/statistics/users`)**
- 新增/流失用户曲线
- 角色分布
- 活跃度分层
- 留存率分析

##### **6.4.3 内容分析 (`/statistics/content`)**
- 阅读 Top 10
- 分类占比
- 完读率统计
- 内容质量评分

##### **6.4.4 练习分析 (`/statistics/practice`)**
- 整体通过率趋势
- 各场景对比
- 分数分布直方图
- 错误模式识别

---

### 6.5 用户管理

**路由前缀**: `/users/*`  
**权限**: 差异化 (见权限矩阵)

#### **子功能**

##### **6.5.1 用户列表 (`/users/list`) [admin]
- **高级搜索**: 用户名、邮箱、角色、状态、注册时间
- **批量操作**: 导出、启用/禁用、发送通知
- **快速操作**: 编辑、重置密码、查看详情

##### **6.5.2 创建用户 (`/users/create`) [admin]
- **表单字段**: 用户名、邮箱、手机、密码、角色
- **学生额外字段**: 学号、专业、学期、指导教师
- **自动生成密码**: 可选，生成后需强制首次登录修改

##### **6.5.3 我的学生 (`/users/students`) [teacher]
- **学生概览卡片**: 总数、平均分、活跃率、需关注人数
- **学生表格**: 基本信息 + 学习数据
- **快速查看**: 点击弹出学生详情侧边栏
- **批量导出**: 成绩单 Excel

##### **6.5.4 个人中心 (`/users/profile`) [所有角色]
- **头像上传**: 支持裁剪
- **基本信息**: 昵称、邮箱、手机
- **修改密码**: 旧密码 + 新密码 + 确认
- **安全设置**: 登录历史、在线设备

---

## 7. API 设计规范

### 7.1 基础约定

- **Base URL**: `http://localhost:8000/api/v1/`
- **认证方式**: JWT Bearer Token (`Authorization: Bearer <token>`)
- **响应格式**: JSON
- **分页**: `?page=1&page_size=20`
- **排序**: `?ordering=-created_at`

### 7.2 统一响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "pagination": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

### 7.3 核心 API 端点

#### **认证模块**

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | `/auth/login/` | 登录获取 token | 公开 |
| POST | `/auth/register/` | 注册 (可选) | 公开 |
| POST | `/auth/logout/` | 注销 (黑名单) | 认证 |
| GET | `/auth/me/` | 当前用户信息 | 认证 |
| PUT | `/auth/password/` | 修改密码 | 认证 |

#### **用户管理**

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | `/users/` | 用户列表 (分页) | admin/teacher |
| POST | `/users/` | 创建用户 | admin |
| GET | `/users/{id}/` | 用户详情 | admin/teacher/self |
| PUT | `/users/{id}/` | 更新用户 | admin/teacher/self |
| DELETE | `/users/{id}/` | 删除用户 | admin |
| GET | `/users/me/students/` | 我的学生列表 | teacher |
| PUT | `/users/{id}/password/reset/` | 重置密码 | admin |

#### **学习内容**

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | `/learning/materials/` | 内容列表 | admin/teacher |
| POST | `/learning/materials/` | 创建内容 | admin/teacher |
| GET | `/learning/materials/{id}/` | 内容详情 | admin/teacher |
| PUT | `/learning/materials/{id}/` | 更新内容 | admin/teacher |
| DELETE | `/learning/materials/{id}/` | 删除内容 | admin/teacher |
| PUT | `/learning/materials/{id}/publish/` | 发布/下架 | admin/teacher |
| POST | `/learning/materials/bulk-delete/` | 批量删除 | admin/teacher |

#### **练习系统**

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | `/practice/scenarios/` | 场景列表 | admin/teacher |
| POST | `/practice/scenarios/` | 创建场景 | admin/teacher |
| GET | `/practice/scenarios/{id}/` | 场景详情 | admin/teacher |
| PUT | `/practice/scenarios/{id}/` | 更新场景 | admin/teacher |
| DELETE | `/practice/scenarios/{id}/` | 删除场景 | admin |
| GET | `/practice/scenarios/{id}/topics/` | 主题列表 | admin/teacher |
| GET | `/practice/records/` | 练习记录列表 | admin/teacher/student* |
| GET | `/practice/records/{id}/` | 记录详情 | admin/teacher/owner |
| GET | `/practice/export/` | 导出报表 | admin/teacher |

#### **数据统计**

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | `/statistics/overview/` | 总览数据 | admin/teacher/student |
| GET | `/statistics/users/` | 用户分析 | admin/teacher |
| GET | `/statistics/content/` | 内容分析 | admin/teacher |
| GET | `/statistics/practice/` | 练习分析 | admin/teacher/student |

> *注: student 只能获取自己的统计数据

---

## 8. 前端架构

### 8.1 状态管理 (Pinia)

```javascript
// src/store/modules/auth.js
import { defineStore } from 'pinia'
import { loginApi, getUserInfo } from '@/api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null,
    role: '',
    isLoggedIn: false
  }),
  
  getters: {
    isAdmin: (state) => state.role === 'admin',
    isTeacher: (state) => ['admin', 'teacher'].includes(state.role),
    isAdminOrTeacher: (state) => ['admin', 'teacher'].includes(state.role)
  },
  
  actions: {
    async login(credentials) {
      const { data } = await loginApi(credentials)
      this.token = data.access
      this.role = data.user.role
      this.isLoggedIn = true
      
      localStorage.setItem('token', this.token)
      
      await this.fetchUserInfo()
    },
    
    async fetchUserInfo() {
      const { data } = await getUserInfo()
      this.user = data
    },
    
    logout() {
      this.token = ''
      this.user = null
      this.role = ''
      this.isLoggedIn = false
      
      localStorage.removeItem('token')
    }
  }
})
```

### 8.2 动态侧边栏菜单

```javascript
// src/config/menu.js
export const menuConfig = {
  admin: [
    {
      path: '/dashboard',
      title: '仪表盘',
      icon: 'Odometer'
    },
    {
      path: '/learning',
      title: '学习管理',
      icon: 'Reading',
      children: [
        { path: '/learning/list', title: '内容列表' },
        { path: '/learning/create', title: '创建内容' }
      ]
    },
    {
      path: '/practice',
      title: '练习系统',
      icon: 'Aim',
      children: [
        { path: '/practice/scenarios', title: '场景管理' },
        { path: '/practice/records', title: '练习记录' }
      ]
    },
    {
      path: '/statistics',
      title: '数据分析',
      icon: 'DataAnalysis'
    },
    {
      path: '/users',
      title: '用户管理',
      icon: 'UserFilled',
      children: [
        { path: '/users/list', title: '用户列表' },
        { path: '/users/roles', title: '角色管理' }
      ]
    },
    {
      path: '/settings',
      title: '系统设置',
      icon: 'Setting'
    }
  ],
  
  teacher: [
    {
      path: '/dashboard',
      title: '仪表盘',
      icon: 'Odometer'
    },
    {
      path: '/learning',
      title: '学习管理',
      icon: 'Reading',
      children: [
        { path: '/learning/list', title: '内容列表' },
        { path: '/learning/create', title: '创建内容' }
      ]
    },
    {
      path: '/practice',
      title: '练习系统',
      icon: 'Aim',
      children: [
        { path: '/practice/scenarios', title: '场景管理' },
        { path: '/practice/records', title: '学生练习记录' },
        { path: '/practice/my-records', title: '我的练习' }
      ]
    },
    {
      path: '/statistics',
      title: '数据分析',
      icon: 'DataAnalysis'
    },
    {
      path: '/users',
      title: '学生管理',
      icon: 'User',
      children: [
        { path: '/users/students', title: '我的学生' }
      ]
    }
  ],
  
  student: [
    {
      path: '/dashboard',
      title: '我的仪表盘',
      icon: 'Odometer'
    },
    {
      path: '/learning',
      title: '课程学习',
      icon: 'Reading'
    },
    {
      path: '/practice',
      title: '我的练习',
      icon: 'Aim',
      children: [
        { path: '/practice/history', title: '练习历史' },
        { path: '/practice/wrong-questions', title: '错题本' }
      ]
    },
    {
      path: '/profile',
      title: '个人中心',
      icon: 'User'
    }
  ]
}
```

### 8.3 API 请求封装

```javascript
// src/api/request.js
import axios from 'axios'
import { useAuthStore } from '@/store/modules/auth'
import { ElMessage } from 'element-plus'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1/',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 自动附加 token
service.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器 - 统一错误处理
service.interceptors.response.use(
  (response) => {
    const res = response.data
    
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      
      // Token 过期 → 自动登出
      if (res.code === 401) {
        const authStore = useAuthStore()
        authStore.logout()
        window.location.href = '/login'
      }
      
      return Promise.reject(new Error(res.message))
    }
    
    return res
  },
  (error) => {
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

export default service
```

---

## 9. 安全性设计

### 9.1 认证安全

- **JWT Token**: Access Token (15min) + Refresh Token (7d)
- **密码加密**: bcrypt (Django 默认)
- **登录限制**: 5次失败后锁定 15 分钟
- **Token 黑名单**: Redis 存储，注销即时生效

### 9.2 授权安全

- **RBAC 权限**: 基于角色的访问控制
- **数据权限**: 中间件自动过滤 QuerySet
- **接口鉴权**: 每个 API 端点都有权限检查
- **前端守卫**: 路由级别 + 按钮级别双重校验

### 9.3 数据安全

- **SQL 注入防护**: ORM 参数化查询
- **XSS 防护**: Django 模板自动转义 + 前端过滤
- **CSRF 防护**: Django CSRF Token (API 模式可禁用)
- **CORS 策略**: 白名单机制，仅允许后台域名

### 9.4 传输安全

- **HTTPS**: 生产环境强制 HTTPS
- **敏感数据加密**: 手机号、邮箱脱敏展示
- **文件上传限制**: 类型白名单 + 大小限制 (5MB)

---

## 10. 部署方案

### 10.1 开发环境

```bash
# 1. 启动后端 API
cd "Prompt Teacher"
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8000

# 2. 启动前端开发服务器
cd admin-panel
npm install
npm run dev
# 访问 http://localhost:5173
```

### 10.2 生产环境

#### **方案 A: Docker Compose (推荐)**

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: prompt_teacher_db
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    command: gunicorn prompt_teaching.wsgi:application --bind 0.0.0.0:8000 --workers 4
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    env_file:
      - .env.production

  frontend:
    build: ./admin-panel
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

#### **方案 B: 传统部署**

```bash
# 后端 (Gunicorn + Nginx)
gunicorn prompt_teaching.wsgi:application --bind 127.0.0.1:8000 --workers 4

# 前端 (Nginx 静态服务)
npm run build
# 将 dist/ 目录内容复制到 Nginx 的 html/ 目录
```

### 10.3 环境变量

```bash
# .env.production
SECRET_KEY=<your-secret-key>
DEBUG=False
ALLOWED_HOSTS=admin.yourdomain.com

# Database
USE_POSTGRES=true
DB_HOST=db
DB_NAME=prompt_teacher_db
DB_USER=admin
DB_PASSWORD=<db-password>

# Redis
REDIS_URL=redis://redis:6379/0

# CORS
CORS_ALLOWED_ORIGINS=https://admin.yourdomain.com

# JWT
JWT_SECRET_KEY=<jwt-secret>
ACCESS_TOKEN_LIFETIME=15  # minutes
REFRESH_TOKEN_LIFETIME=7  # days
```

---

## 📌 附录

### A. 依赖清单

#### **Python (requirements.txt)**
```
Django==6.0.4
djangorestframework==3.15.x
djangorestframework-simplejwt==5.x
django-cors-headers==4.x
psycopg2-binary==2.9.x
redis==5.x
Pillow==10.x  # 图片处理
django-filter==24.x  # 高级筛选
drf-spectacular==0.27.x  # API 文档 (可选)
```

#### **Node.js (package.json)**
```json
{
  "dependencies": {
    "vue": "^3.4",
    "vue-router": "^4",
    "pinia": "^2",
    "element-plus": "^2",
    "@element-plus/icons-vue": "^2",
    "axios": "^1",
    "echarts": "^5",
    "md-editor-v3": "^4",
    "nprogress": "^0.2",  # 进度条
    "dayjs": "^1"  // 日期处理
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5",
    "vite": "^5",
    "sass": "^1",
    "unplugin-auto-import": "^0.17",
    "unplugin-vue-components": "^0.26"
  }
}
```

### B. 开发里程碑

| 阶段 | 任务 | 预估工作量 |
|------|------|-----------|
| **Phase 1** | 项目初始化 + 用户认证 | 2 天 |
| **Phase 2** | 用户管理 + 权限系统 | 3 天 |
| **Phase 3** | 学习内容管理 | 2 天 |
| **Phase 4** | 练习系统管理 | 3 天 |
| **Phase 5** | 数据统计分析 | 3 天 |
| **Phase 6** | Dashboard 优化 | 2 天 |
| **Phase 7** | 测试 + Bug 修复 | 2 天 |
| **Phase 8** | 部署上线 | 1 天 |
| **总计** | | **18 天** |

### C. 参考资料

- [Django REST Framework 官方文档](https://www.django-rest-framework.org/)
- [Vue 3 官方文档](https://cn.vuejs.org/)
- [Element Plus 组件库](https://element-plus.org/)
- [ECharts 图表库](https://echarts.apache.org/zh/)
- [JWT 认证最佳实践](https://jwt.io/introduction)

---

## ✅ 文档状态

- **版本**: v1.0 Final
- **最后更新**: 2026-05-30
- **审核状态**: ✅ 用户已确认
- **下一步**: 过渡到实施计划 (writing-plans skill)

---

**文档结束** 🎉
