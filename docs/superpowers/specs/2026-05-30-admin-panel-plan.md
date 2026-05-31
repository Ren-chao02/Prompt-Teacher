# Prompt Teacher 后台管理系统 - 实施计划

**项目名称**: Prompt Teacher Admin Panel  
**版本**: v1.0 Implementation Plan  
**日期**: 2026-05-30  
**基于**: [2026-05-30-admin-panel-design.md](./2026-05-30-admin-panel-design.md)  
**状态**: 🚀 待执行  

---

## 📋 目录

1. [实施概览](#1-实施概览)
2. [环境准备](#2-环境准备)
3. [Phase 1: 项目初始化与认证](#3-phase-1-项目初始化与认证)
4. [Phase 2: 用户管理与权限](#4-phase-2-用户管理与权限)
5. [Phase 3: 学习内容管理](#5-phase-3-学习内容管理)
6. [Phase 4: 练习系统管理](#6-phase-4-练习系统管理)
7. [Phase 5: 数据统计分析](#7-phase-5-数据统计分析)
8. [Phase 6: Dashboard 优化](#8-phase-6-dashboard-优化)
9. [Phase 7: 测试与质量保障](#9-phase-7-测试与质量保障)
10. [Phase 10: 部署上线](#10-phase-10-部署上线)
11. [增强点实施计划](#11-增强点实施计划)
12. [风险控制](#12-风险控制)

---

## 1. 实施概览

### 1.1 时间线

```
Week 1 (Day 1-5):
├── Day 1-2:   Phase 1 - 项目初始化 + 认证 (+ API 文档)
├── Day 3-5:   Phase 2 - 用户管理 + 权限 (+ 操作日志)
│
Week 2 (Day 6-10):
├── Day 6-7:   Phase 3 - 学习内容管理
├── Day 8-10:  Phase 4 - 练习系统管理 (+ WebSocket 通知)
│
Week 3 (Day 11-17):
├── Day 11-13: Phase 5 - 数据统计分析
├── Day 14-15: Phase 6 - Dashboard 优化 (+ i18n)
├── Day 16-17: Phase 7 - 测试 + Bug 修复 (单元测试)
│
Week 4 (Day 18-21):
└── Day 18-21: Phase 8 - 部署上线 + 文档收尾
```

### 1.2 技术栈确认

**后端**:
- Python 3.11+
- Django 6.0.4
- Django REST Framework 3.15.x
- PostgreSQL 15+ / SQLite (dev)
- Redis 7.x (缓存/会话/WebSocket)

**前端**:
- Node.js 18+
- Vue 3.4+ (Composition API)
- Vite 5.x
- Element Plus 2.x
- ECharts 5.x
- Pinia 2.x

---

## 2. 环境准备

### 2.1 后端环境搭建

```bash
# 1. 创建虚拟环境
cd "/home/mjl/Prompt Teacher"
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 2. 升级 pip
pip install --upgrade pip

# 3. 安装依赖
pip install -r requirements.txt

# 4. (可选) 创建 .env 文件
cp .env.example .env.production
```

#### **requirements.txt 更新**
```txt
# 现有依赖保持不变
# 新增以下包:

# REST Framework
djangorestframework==3.15.2
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.0
django-filter==24.2

# 数据库
psycopg2-binary==2.9.9  # PostgreSQL 适配器

# 缓存 & 会话
redis==5.0.1
channels==4.0.0  # WebSocket 支持
channels-redis==4.1.0

# API 文档 (增强点 #1)
drf-spectacular==0.27.2

# 操作日志 (增强点 #2)
django-simple-history==3.5.0

# 开发工具
pytest==8.1.1
pytest-django==4.8.0
pytest-cov==5.0.0
black==24.4.2  # 代码格式化
flake8==7.0.0  # 代码检查
```

### 2.2 前端环境搭建

```bash
# 1. 创建 Vue 3 项目
cd "/home/mjl/Prompt Teacher"
npm create vite@latest admin-panel -- --template vue

# 2. 进入项目目录
cd admin-panel

# 3. 安装核心依赖
npm install vue-router@4
npm install pinia@2
npm install element-plus@2
npm install @element-plus/icons-vue@2
npm install axios@1
npm install echarts@5
npm install md-editor-v3@4
npm install nprogress@0.2
npm install dayjs@1

# 4. 安装开发依赖
npm install -D sass@1
npm install -D unplugin-auto-import@0.17
npm install -D unplugin-vue-components@0.26

# 5. 启动开发服务器
npm run dev
# 访问 http://localhost:5173
```

### 2.3 配置文件准备

#### **后端 settings.py 关键配置**

```python
# prompt_teaching/settings.py 新增配置

INSTALLED_APPS = [
    # ... 现有应用保持不变 ...
    
    # 新增 DRF 相关
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    
    # 新增第三方应用
    'django_filters',
    
    # 增强点
    'drf_spectacular',          # API 文档
    'simple_history',           # 操作日志
    
    # WebSocket
    'channels',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS 必须在最前
    # ... 其他中间件 ...
]

# REST Framework 配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',  # API 文档
}

# JWT 配置
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

# CORS 配置
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vue dev server
    "https://admin.yourdomain.com",  # 生产域名
]
CORS_ALLOW_CREDENTIALS = True

# 自定义用户模型
AUTH_USER_MODEL = 'users.UserProfile'

# Redis 配置
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

# API 文档配置
SPECTACULAR_SETTINGS = {
    'TITLE': 'Prompt Teacher API',
    'DESCRIPTION': '后台管理系统 API 文档',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
```

#### **前端环境变量**

```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000/api/v1/
VITE_APP_TITLE=Prompt Teacher Admin
VITE_WS_URL=ws://localhost:8000/ws/

# .env.production
VITE_API_BASE_URL=https://api.yourdomain.com/api/v1/
VITE_APP_TITLE=Prompt Teacher Admin
VITE_WS_URL=wss://api.yourdomain.com/ws/
```

---

## 3. Phase 1: 项目初始化与认证

**⏱️ 时间**: 2 天 (+ 0.5 天 API 文档)  
**📅 日期**: Day 1-2  
**✅ 交付物**: 可登录的后台框架

### 3.1 任务清单

#### **Day 1: 后端基础架构**

- [ ] **1.1 创建 Django 应用结构**
  ```bash
  python manage.py startapp users
  mkdir -p users/api learning/api practice/api core/api
  ```

- [ ] **1.2 实现 UserProfile 模型**
  - 文件: `users/models.py`
  - 参考: 设计规范第 4 章
  - 字段: role, phone, avatar, student_id, semester, major, teacher(FK)

- [ ] **1.3 配置自定义用户模型**
  ```python
  # settings.py
  AUTH_USER_MODEL = 'users.UserProfile'
  ```

- [ ] **1.4 数据库迁移**
  ```bash
  python manage.py makemigrations users
  python manage.py migrate
  ```

- [ ] **1.5 创建超级管理员账号**
  ```bash
  python manage.py createsuperuser
  ```

#### **Day 2: JWT 认证系统**

- [ ] **1.6 实现 JWT 认证 API**
  - 文件: `users/api/views.py`
  - 端点:
    - `POST /auth/login/` - 登录获取 token
    - `POST /auth/refresh/` - 刷新 token
    - `POST /auth/logout/` - 注销 (黑名单)
    - `GET /auth/me/` - 当前用户信息

- [ ] **1.7 创建用户序列化器**
  - 文件: `users/serializers.py`
  - 序列化器:
    - `LoginSerializer` - 登录验证
    - `UserSerializer` - 用户信息 (CRUD)
    - `UserProfileSerializer` - 详细信息

- [ ] **1.8 配置 URL 路由**
  - 文件: `users/api/urls.py`, `prompt_teaching/urls.py`
  - 路径: `/api/v1/auth/*`, `/api/v1/users/*`

- [ ] **1.9 CORS 跨域配置完成**
  - 验证: 前端可成功请求后端 API

#### **增强点 #1: API 文档自动生成** (+0.5天)

- [ ] **1.10 安装 drf-spectacular**
  ```bash
  pip install drf-spectacular
  ```

- [ ] **1.11 配置 Swagger UI**
  - 添加到 `INSTALLED_APPS`
  - 配置 `SPECTACULAR_SETTINGS` (见上方)
  - 添加 URL: `/api/schema/`, `/api/docs/`

- [ ] **1.12 为所有 ViewSet 添加 docstring**
  - 示例:
  ```python
  class UserViewSet(viewsets.ModelViewSet):
      """
      retrieve: 返回用户实例
      list: 返回用户列表
      create: 创建新用户
      update: 更新用户信息
      partial_update: 部分更新
      destroy: 删除用户
      """
  ```

### 3.2 验证标准

- [ ] 可以通过 Postman/curl 成功登录获取 JWT Token
- [ ] 使用 Token 可以访问 `/auth/me/` 获取用户信息
- [ ] Token 过期能正确返回 401 错误
- [ ] Swagger UI 可访问: `http://localhost:8000/api/docs/`
- [ ] 前端 Vue 项目可以正常启动 (`npm run dev`)

---

## 4. Phase 2: 用户管理与权限

**⏱️ 时间**: 3 天 (+ 0.5 天 操作日志)  
**📅 日期**: Day 3-5  
**✅ 交付物**: 完整的用户 CRUD + RBAC 权限系统

### 4.1 任务清单

#### **Day 3: 权限类 + 中间件**

- [ ] **2.1 实现自定义权限类**
  - 文件: `users/permissions.py`
  - 类:
    - `IsAdmin` - 仅管理员
    - `IsTeacher` - 教师及以上
    - `IsStudentOrAbove` - 所有认证用户
    - `IsOwnerOrReadOnly` - 所有者可写

- [ ] **2.2 实现数据权限中间件**
  - 文件: `users/middleware.py`
  - 功能:
    - 自动过滤 QuerySet (admin→全部, teacher→自己+学生, student→自己)
    - 通过 `request.user.get_filtered_queryset(model)` 调用

- [ ] **2.3 注册中间件**
  ```python
  # settings.py
  MIDDLEWARE = [
      'users.middleware.DataPermissionMiddleware',
      # ...
  ]
  ```

#### **Day 4: 用户管理 API**

- [ ] **2.4 实现 UserViewSet**
  - 文件: `users/api/views.py`
  - 功能:
    - GET `/users/` - 用户列表 (分页、筛选、搜索)
    - POST `/users/` - 创建用户
    - GET `/users/{id}/` - 用户详情
    - PUT `/users/{id}/` - 更新用户
    - DELETE `/users/{id}/` - 删除用户
    - PUT `/users/{id}/password/reset/` - 重置密码
    - GET `/users/me/students/` - 我的学生 (教师专用)

- [ ] **2.5 配置动态权限**
  ```python
  class UserViewSet(viewsets.ModelViewSet):
      def get_permissions(self):
          if self.action == 'create':
              return [IsAdmin()]
          if self.action in ['update', 'partial_update', 'destroy']:
              return [IsAdmin() | IsOwner()]
          return [IsAuthenticated()]
  ```

- [ ] **2.6 实现批量操作**
  - 批量删除: `POST /users/bulk-delete/`
  - 批量导出: `GET /users/export/?format=excel`

#### **Day 5: 前端用户模块**

- [ ] **2.7 实现登录页面**
  - 文件: `src/views/login/index.vue`
  - 功能:
    - 用户名/密码表单
    - 表单验证 (Element Plus Form)
    - 登录成功 → 存储 Token → 跳转 Dashboard
    - 记住我选项

- [ ] **2.8 实现用户列表页**
  - 文件: `src/views/user/list.vue`
  - 功能:
    - 搜索栏 (用户名、角色、状态筛选)
    - 数据表格 (el-table)
    - 分页组件
    - 批量操作按钮
    - 创建/编辑/删除按钮

- [ ] **2.9 实现个人中心页**
  - 文件: `src/views/user/profile.vue`
  - 功能:
    - 头像上传 (裁剪预览)
    - 基本信息编辑
    - 修改密码表单
    - 登录历史展示

- [ ] **2.10 实现布局组件**
  - 文件: `src/components/Layout/AdminLayout.vue`
  - 组件:
    - Sidebar (侧边栏, 动态菜单)
    - Navbar (顶栏, 用户信息下拉)
    - Breadcrumb (面包屑导航)
    - TagsView (标签页导航, 可选)

#### **增强点 #2: 操作日志审计** (+0.5天)

- [ ] **2.11 安装 django-simple-history**
  ```bash
  pip install django-simple-history
  ```

- [ ] **2.12 为关键模型添加审计字段**
  ```python
  # users/models.py
  from simple_history.models import HistoricalRecords
  
  class UserProfile(AbstractUser, HistoricalRecords):
      history = HistoricalRecords(
          inherited=True,
          excluded_fields=['password', 'last_login']
      )
  ```

- [ ] **2.13 实现操作日志查看 API**
  - 端点: `GET /audit-logs/`
  - 功能: 按用户、时间范围、操作类型筛选
  - 展示: 谁、什么时间、做了什么、变更前后值

- [ ] **2.14 前端操作日志页面**
  - 文件: `src/views/system/audit-logs.vue`
  - 表格展示 + 高级筛选

### 4.2 验证标准

- [ ] 不同角色登录后看到不同的菜单
- [ ] 管理员可以创建/编辑/删除任何用户
- [ ] 教师只能看到自己的学生列表
- [ ] 学生只能访问个人中心，看不到用户管理菜单
- [ ] 操作日志能记录关键操作的完整变更
- [ ] Swagger 文档更新了新 API

---

## 5. Phase 3: 学习内容管理

**⏱️ 时间**: 2 天  
**📅 日期**: Day 6-7  
**✅ 交付物**: 学习资料的完整 CRUD 功能

### 5.1 任务清单

#### **Day 6: 后端 API**

- [ ] **3.1 实现 LearningMaterialViewSet**
  - 文件: `learning/api/views.py`
  - 端点:
    - GET/POST `/learning/materials/`
    - GET/PUT/DELETE `/learning/materials/{id}/`
    - PUT `/learning/materials/{id}/publish/` - 发布/下架
    - POST `/learning/materials/bulk-delete/` - 批量删除

- [ ] **3.2 创建学习资料序列化器**
  - 文件: `learning/api/serializers.py`
  - 字段验证 (标题长度、分类合法性)
  - Markdown 内容处理

- [ ] **3.3 实现高级筛选**
  - 支持按分类、状态、关键词搜索
  - 支持排序 (创建时间、阅读量、排序权重)

- [ ] **3.4 添加权限控制**
  - admin/teacher: 全部读写权限
  - student: 只读 (如果需要)

#### **Day 7: 前端页面**

- [ ] **3.5 实现学习内容列表页**
  - 文件: `src/views/learning/list.vue`
  - 功能:
    - 搜索栏 (标题、分类 Select、状态 Switch)
    - 排序选择器
    - 表格列: 标题、分类(Badge)、排序、阅读量、状态(Switch)、操作
    - 批量操作 (删除、修改分类)
    - 分页

- [ ] **3.6 实现内容编辑页**
  - 文件: `src/views/learning/edit.vue`
  - 功能:
    - 基本信息: 标题 Input、分类 Select、排序 NumberInput、状态 Switch
    - Markdown 编辑器 (md-editor-v3)
    - 左右分屏预览
    - 自动保存 (每 30 秒 localStorage)
    - 保存草稿 / 发布按钮

- [ ] **3.7 实现内容详情页**
  - 文件: `src/views/learning/detail.vue`
  - 功能:
    - Markdown 渲染展示 (只读)
    - 元信息卡片 (作者、创建时间、阅读量)
    - 操作按钮 (编辑、删除、复制)

### 5.2 验证标准

- [ ] 可以创建新的学习资料 (含 Markdown 内容)
- [ ] 可以编辑已有内容并保存
- [ ] 可以发布/下架内容
- [ ] 列表页支持搜索、筛选、排序、分页
- [ ] Markdown 编辑器正常工作 (预览同步)
- [ ] 批量删除功能正常

---

## 6. Phase 4: 练习系统管理

**⏱️ 时间**: 3 天 (+ 1 天 WebSocket)  
**📅 日期**: Day 8-10  
**✅ 交付物**: 场景/主题/记录的完整管理

### 6.1 任务清单

#### **Day 8: 场景和主题管理**

- [ ] **4.1 实现 PracticeScenarioViewSet**
  - 文件: `practice/api/views.py`
  - CRUD + 启用/禁用开关
  - 拖拽排序接口

- [ ] **4.2 实现 PracticeTopicViewSet**
  - 嵌套在场景下: `/practice/scenarios/{id}/topics/`
  - 评估标准的 JSON Schema 验证

- [ ] **4.3 场景管理前端页面**
  - 文件: `src/views/practice/scenarios.vue`
  - 卡片式布局 (图标 + 标题 + 描述 + 难度 Badge)
  - 创建/编辑对话框 (Dialog)
  - 启用/禁用 Switch
  - 拖拽排序 (vuedraggable 库)

- [ ] **4.4 主题管理前端页面**
  - 文件: `src/views/practice/topics.vue`
  - 嵌套表格 (属于某场景的主题列表)
  - 内联编辑 (点击单元格直接编辑)
  - 评估标准 JSON Editor (jsoneditor 库)

#### **Day 9: 练习记录管理**

- [ ] **4.5 实现 PracticeRecordViewSet**
  - 文件: `practice/api/views.py`
  - 高级筛选 (时间、用户、场景、分数区间)
  - 详情接口 (完整输入输出 + 评分明细)
  - 导出接口 (Excel/PDF)

- [ ] **4.6 练习记录列表页**
  - 文件: `src/views/practice/records.vue`
  - 高级筛选面板 (折叠/展开)
  - 表格: 用户、场景、得分(颜色标识)、用时、操作
  - 详情弹窗 (Drawer 侧边栏)
  - 导出按钮

- [ ] **4.7 我的练习页 (学生)**
  - 文件: `src/views/practice/my-records.vue`
  - 个人练习历史列表
  - 成绩统计卡片 (平均分、最高分)
  - 进步曲线图 (ECharts 折线图)
  - 错题本 Tab (得分 < 70 的汇总)

#### **Day 10: 教师视角 + 增强**

- [ ] **4.8 我的学生练习数据**
  - 教师视角: 仅显示自己学生的记录
  - 学生概览卡片 (总数、平均分、活跃率)
  - 点击学生 → 弹出该学生详细数据侧边栏

- [ ] **4.9 批量导出成绩单**
  - 选择学生/时间范围
  - 生成 Excel (使用 xlsx 库)
  - 包含: 学号、姓名、各场景得分、平均分

#### **增强点 #4: 实时通知系统 (WebSocket)** (+1天)

- [ ] **4.10 后端 WebSocket 配置**
  - 安装 channels + channels-redis
  - 配置 ASGI (替代 WSGI)
  - 创建 Consumer: `practice/consumers.py`
  - 功能: 新练习提交时推送通知给教师

- [ ] **4.11 前端 WebSocket 客户端**
  - 文件: `src/utils/websocket.js`
  - 自动重连机制
  - 心跳检测

- [ ] **4.12 通知中心组件**
  - 文件: `src/components/Common/NotificationBell.vue`
  - 顶部导航栏铃铛图标
  - 未读数量 Badge
  - 下拉面板显示最近通知
  - 点击跳转到对应记录

### 6.2 验证标准

- [ ] 可以创建/编辑/删除场景和主题
- [ ] 场景支持拖拽排序
- [ ] 评估标准可以用 JSON Editor 编辑
- [ ] 练习记录列表支持多维度筛选
- [ ] 教师只能看到自己学生的数据
- [ ] 学生只能看到自己的练习记录
- [ ] 新练习提交时教师收到实时通知 (WebSocket)
- [ ] 导出 Excel 功能正常

---

## 7. Phase 5: 数据统计分析

**⏱️ 时间**: 3 天  
**📅 日期**: Day 11-13  
**✅ 交付物**: 4 个维度的可视化数据分析

### 7.1 任务清单

#### **Day 11: 统计 API 开发**

- [ ] **5.1 实现统计数据聚合查询**
  - 文件: `core/api/views.py`
  - 视图类:
    - `StatisticsOverviewAPIView` - 总览数据
    - `UserStatisticsAPIView` - 用户分析
    - `ContentStatisticsAPIView` - 内容分析
    - `PracticeStatisticsAPIView` - 练习分析
  
  - 优化技巧:
    - 使用 `annotate()` + `aggregate()` 减少数据库查询
    - 使用 `select_related()` / `prefetch_related()` 优化关联查询
    - Redis 缓存热点数据 (TTL 5 分钟)

- [ ] **5.2 数据权限过滤**
  - admin: 全局统计
  - teacher: 所教学生统计
  - student: 个人统计
  - 复用 DataPermissionMiddleware

#### **Day 12: 图表页面实现**

- [ ] **5.3 总览面板页面**
  - 文件: `src/views/statistics/overview.vue`
  - 4 个统计卡片 (el-statistic 或自定义 StatCard)
  - 学习趋势折线图 (ECharts line)
  - 练习分布饼图 (ECharts pie)
  - 用户活跃柱状图 (ECharts bar)

- [ ] **5.4 用户分析页面**
  - 文件: `src/views/statistics/users.vue`
  - 新增/流失双轴图
  - 角色分布环形图
  - 留存率漏斗图 (可选)
  - 用户排行表格

- [ ] **5.5 内容分析页面**
  - 文件: `src/views/statistics/content.vue`
  - 阅读 Top 10 水平条形图
  - 分类占比饼图
  - 完读率趋势线
  - 内容质量评分雷达图

#### **Day 13: 练习分析 + 交互优化**

- [ ] **5.6 练习分析页面**
  - 文件: `src/views/statistics/practice.vue`
  - 通过率趋势面积图
  - 各场景对比分组柱状图
  - 分数分布直方图
  - 错误模式词云图 (可选)

- [ ] **5.7 图表交互功能**
  - 时间范围切换 (日/周/月/年) - 全局组件
  - 图表联动 (点击某个图表，其他图表联动筛选)
  - 数据导出 (图表数据导出为 CSV)
  - 图表全屏/刷新/下载图片

- [ ] **5.8 ECharts 封装组件**
  - 文件: `src/components/Common/BaseChart.vue`
  - Props: options, height, autoResize
  - 统一 loading 状态
  - 统一错误处理
  - 响应式尺寸自适应

### 7.2 验证标准

- [ ] 4 个统计页面都能正确展示数据
- [ ] 图表渲染流畅无报错
- [ ] 时间范围切换正常工作
- [ ] 不同角色看到的数据范围正确
- [ ] 图表支持交互 (tooltip、legend 切换等)
- [ ] 数据缓存生效 (重复请求变快)

---

## 8. Phase 6: Dashboard 优化

**⏱️ 时间**: 2 天 (+ 0.5 天 i18n)  
**📅 日期**: Day 14-15  
**✅ 交付物**: 个性化的智能仪表盘

### 8.1 任务清单

#### **Day 14: Dashboard 核心功能**

- [ ] **6.1 动态 Dashboard API**
  - 文件: `core/api/views.py`
  - 根据 user.role 返回不同数据:
    - admin: 全局指标 + 待处理事项
    - teacher: 所教学生概况 + 最近练习
    - student: 个人学习进度 + 推荐内容

- [ ] **6.2 Dashboard 页面实现**
  - 文件: `src/views/dashboard/index.vue`
  - 组件:
    - WelcomeBanner (欢迎语 + 角色 Badge + 日期)
    - StatCardsRow (4个核心指标卡片)
    - ChartsGrid (2x2 图表网格)
    - QuickActions (快捷入口按钮组)
    - RecentActivities (最近活动动态流)

- [ ] **6.3 待处理事项组件**
  - 文件: `src/components/Dashboard/PendingItems.vue`
  - 类型:
    - 待审核的练习记录 (教师)
    - 新用户待分配 (管理员)
    - 系统备份提醒 (管理员)
  - 数量 Badge + 点击跳转

- [ ] **6.4 快捷入口配置**
  - 根据角色动态生成常用操作
  - admin: 创建内容、用户管理、系统设置
  - teacher: 创建内容、查看学生、导出报表
  - student: 开始学习、查看练习、错题本

#### **Day 15: 个性化 + 增强**

- [ ] **6.5 Dashboard 可定制性**
  - 拖拽调整卡片位置 (vuedraggable)
  - 卡片折叠/展开
  - 布局保存到 localStorage / 后端偏好设置
  - 重置为默认布局

- [ ] **6.6 性能优化**
  - 懒加载非首屏图表
  - 虚拟滚动 (最近活动列表过长时)
  - Skeleton 骨架屏加载态
  - 防抖搜索 (统计页全局筛选)

#### **增强点 #5: 国际化支持 (i18n)** (+0.5天)

- [ ] **6.7 安装 vue-i18n**
  ```bash
  npm install vue-i18n@9
  ```

- [ ] **6.8 创建语言包**
  ```
  src/locales/
  ├── zh-CN.json     # 中文 (默认)
  └── en-US.json     # 英文
  ```
  - 翻译所有界面文本 (菜单、按钮、提示、表单标签)

- [ ] **6.9 语言切换组件**
  - 文件: `src/components/Common/LangSwitch.vue`
  - 位置: Navbar 右上角
  - 切换后立即生效 (无需刷新)
  - 语言偏好保存到 localStorage

- [ ] **6.10 Element Plus 国际化**
  ```javascript
  // main.js
  import zhCn from 'element-plus/es/locale/lang/zh-cn'
  import en from 'element-plus/es/locale/lang/en'
  
  const app = createApp(App)
  app.use(ElementPlus, { locale: currentLocale === 'zh' ? zhCn : en })
  ```

### 8.2 验证标准

- [ ] 三种角色看到不同的 Dashboard 内容
- [ ] 统计卡片数据准确且实时更新
- [ ] 图表渲染无误且交互流畅
- [ ] 待处理事项数量准确
- [ ] 快捷入口可用且跳转正确
- [ ] Dashboard 布局可拖拽调整
- [ ] 中英文切换正常工作 (i18n)

---

## 9. Phase 7: 测试与质量保障

**⏱️ 时间**: 2 天 (+ 1 天单元测试)  
**📅 日期**: Day 16-17  
**✅ 交付物**: 80%+ 测试覆盖率 + 零 Critical Bug

### 9.1 任务清单

#### **Day 16: 单元测试 (增强点 #3)**

- [ ] **7.1 配置 pytest 环境**
  ```bash
  pip install pytest pytest-django pytest-cov
  ```
  - 文件: `pytest.ini`, `conftest.py`
  - 配置数据库测试 (SQLite memory)

- [ ] **7.2 编写模型测试**
  - 目录: `users/tests/`, `learning/tests/`, `practice/tests/`
  - 覆盖:
    - UserProfile 字段验证
    - 师生关系约束
    - LearningMaterial 方法
    - PracticeRecord 计算

- [ ] **7.3 编写 API 测试**
  - 目录: `users/api/tests/`, `learning/api/tests/`, ...
  - 覆盖:
    - 认证流程 (登录/刷新/注销)
    - 权限控制 (不同角色的访问限制)
    - CRUD 操作 (正常流程 + 异常情况)
    - 数据权限 (教师只能看自己的学生)
    - 输入验证 (非法数据拒绝)

- [ ] **7.4 编写前端单元测试 (可选)**
  ```bash
  npm install -D vitest @vue/test-utils
  ```
  - Pinia store 测试
  - 工具函数测试
  - 组件渲染测试 (关键组件)

#### **Day 17: 集成测试 + Bug 修复**

- [ ] **7.5 端到端测试 (手动)**
  - 完整业务流程走查:
    1. 注册 → 登录 → 查看 Dashboard
    2. 创建学习资料 → 发布 → 前台查看
    3. 教师创建场景 → 学生练习 → 教师查看记录
    4. 管理员查看统计 → 导出报表
  - 记录所有 Bug 到 Issue Tracker

- [ ] **7.6 性能测试**
  - 使用 Django Debug Toolbar 分析慢查询
  - 使用 Lighthouse 评估前端性能
  - 目标:
    - API 响应 < 200ms (P95)
    - 首屏加载 < 2s
    - Lighthouse Score > 90

- [ ] **7.7 安全测试**
  - SQL 注入尝试 (ORM 应防护)
  - XSS 攻击尝试 (前端过滤)
  - CSRF 验证
  - 权限越权尝试 (直接访问未授权 API)

- [ ] **7.8 Bug 修复循环**
  - 优先级: Critical > Major > Minor
  - 修复后补充回归测试
  - 目标: 0 Critical, 0 Major

#### **增强点 #3: 单元测试目标**

```bash
# 运行测试并生成覆盖率报告
pytest --cov=users --cov=learning --cov=practice --cov-report=html

# 目标覆盖率
├── users/models.py:       95%+
├── users/permissions.py:  100%
├── users/api/views.py:    90%+
├── learning/api/views.py: 85%+
├── practice/api/views.py: 85%+
└── core/api/views.py:     80%+

# 总体目标: 80%+
```

### 9.2 验证标准

- [ ] pytest 运行通过，无失败用例
- [ ] 测试覆盖率达到 80%+
- [ ] 所有 Critical/Major Bug 已修复
- [ ] 性能指标达标 (API < 200ms, FCP < 2s)
- [ ] 安全扫描无高危漏洞
- [ ] 手动端到端测试全部通过

---

## 10. Phase 10: 部署上线

**⏱️ 时间**: 2 天  
**📅 日期**: Day 18-19 (或 Day 20-21)  
**✅ 交付物**: 生产环境可用的后台系统

### 10.1 任务清单

#### **Day 18: Docker 化 + 部署准备**

- [ ] **8.1 编写 Dockerfile**
  ```dockerfile
  # backend/Dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY . .
  CMD ["gunicorn", "prompt_teaching.wsgi:application", "--bind", "0.0.0.0:8000"]
  ```

  ```dockerfile
  # admin-panel/Dockerfile
  FROM node:18-alpine AS builder
  WORKDIR /app
  COPY package*.json ./
  RUN npm ci
  COPY . .
  RUN npm run build
  
  FROM nginx:alpine
  COPY --from=builder /app/dist /usr/share/nginx/html
  EXPOSE 80
  CMD ["nginx", "-g", "daemon off;"]
  ```

- [ ] **8.2 编写 docker-compose.yml**
  - 服务: db (PostgreSQL), redis, backend, frontend
  - 网络: 内部网络隔离
  - 卷: 数据持久化
  - 环境变量: 从 .env.production 读取

- [ ] **8.3 Nginx 配置**
  - 反向代理 (API → Gunicorn)
  - 静态文件服务 (前端 dist)
  - HTTPS (Let's Encrypt 或自有证书)
  - Gzip 压缩
  - 缓存策略 (静态资源长期缓存)

- [ ] **8.4 数据库迁移生产环境**
  ```bash
  # 备份现有数据库
  pg_dump old_db > backup.sql
  
  # 应用迁移
  python manage.py migrate
  
  # 创建初始超级管理员
  python manage.py createsuperuser --noinput \
    --username=admin \
    --email=admin@example.com
  ```

#### **Day 19: 上线 + 监控**

- [ ] **8.5 域名 + DNS 配置**
  - API 域名: api.yourdomain.com
  - Admin 域名: admin.yourdomain.com
  - DNS A 记录指向服务器 IP

- [ ] **8.6 SSL 证书**
  ```bash
  # Let's Encrypt (推荐)
  certbot --nginx -d api.yourdomain.com -d admin.yourdomain.com
  ```

- [ ] **8.7 日志收集**
  - Gunicorn access/error logs
  - Nginx access/error logs
  - Django logging (file handler)
  - 前端错误上报 (Sentry 可选)

- [ ] **8.8 监控告警**
  - Uptime monitoring (UptimeRobot / 自建)
  - Server metrics (CPU/RAM/Disk) - Prometheus + Grafana (可选)
  - Error alerting (邮件/钉钉/企业微信)

- [ ] **8.9 备份策略**
  - 数据库自动备份 (每日凌晨, pg_cron)
  - 保留 30 天备份
  - 异地备份 (对象存储 S3/OSS)

- [ ] **8.10 上线检查清单**
  - [ ] 所有 API 端点可达
  - [ ] 前端页面正常加载
  - [ ] 登录/登出流程正常
  - [ ] 不同角色权限正确
  - [ ] 文件上传/下载正常
  - [ ] HTTPS 生效
  - [ ] 移动端适配正常 (响应式)
  - [ ] 浏览器兼容性 (Chrome/Firefox/Safari/Edge)

### 10.2 验证标准

- [ ] `docker-compose up -d` 一键启动成功
- [ ] 所有容器运行正常 (`docker ps`)
- [ ] 生产环境可通过域名访问
- [ ] HTTPS 证书有效
- [ ] 数据库备份自动化运行
- [ ] 监控告警配置完成
- [ ] 上线检查清单全部通过

---

## 11. 增强点实施计划总结

| # | 增强功能 | 插入阶段 | 额外工作量 | 优先级 | 状态 |
|---|---------|---------|-----------|--------|------|
| 1 | **API 文档 (Swagger)** | Phase 1 | +0.5 天 | 中 | ⏳ 待实施 |
| 2 | **操作日志审计** | Phase 2 | +0.5 天 | 低 | ⏳ 待实施 |
| 3 | **单元测试 (80%+)** | Phase 7 | +1 天 | 高 | ⏳ 待实施 |
| 4 | **实时通知 (WebSocket)** | Phase 4 | +1 天 | 低 | ⏳ 待实施 |
| 5 | **国际化 (i18n)** | Phase 6 | +0.5 天 | 低 | ⏳ 待实施 |

**增强点总计**: +3.5 天

---

## 12. 风险控制

### 12.1 技术风险

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|---------|
| Django 版本兼容性问题 | 中 | 高 | 先在测试环境验证，锁定依赖版本 |
| WebSocket 部署复杂度高 | 中 | 中 | 使用 Daphine ASGI 服务器，参考官方文档 |
| 前端构建体积过大 | 低 | 中 | 代码分割、懒加载、Tree Shaking |
| 数据库性能瓶颈 | 低 | 高 | 添加索引、查询优化、Redis 缓存 |
| 第三方库安全漏洞 | 低 | 高 | 定期 `pip audit` + `npm audit` |

### 12.2 进度风险

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|---------|
| 需求变更 | 中 | 高 | 保持模块化设计，影响范围可控 |
| 技术难题卡壳 | 低 | 中 | 预留 1-2 天 buffer time |
| 测试发现大量 Bug | 中 | 中 | TDD 开发模式，边写边测 |
| 部署环境问题 | 低 | 高 | 尽早准备生产环境镜像测试 |

### 12.3 Buffer Time 建议

- **总工期**: 18 天 (核心) + 3.5 天 (增强) = 21.5 天
- **建议 Buffer**: +2 天 (应对不可预见问题)
- **最终预估**: **23.5 天 (~3.5 周)**

---

## 📊 交付物清单

### **代码交付**

```
Prompt Teacher/
├── backend/                          # Django API 服务 (已完善)
│   ├── users/                        # ✅ 用户认证 + 权限 + 审计
│   ├── learning/api/                 # ✅ 学习内容 API
│   ├── practice/api/                 # ✅ 练习系统 API
│   ├── core/api/                     # ✅ 统计数据 API
│   └── tests/                        # ✅ 单元测试 (80%+ 覆盖)
│
├── admin-panel/                      # Vue 3 前端 (新建)
│   ├── src/
│   │   ├── api/                      # ✅ Axios 封装
│   │   ├── views/                    # ✅ 5大模块页面
│   │   ├── components/               # ✅ 布局 + 通用组件
│   │   ├── router/                   # ✅ 路由 + 守卫
│   │   ├── store/                    # ✅ Pinia 状态管理
│   │   └── locales/                  # ✅ i18n 语言包
│   └── dist/                         # ✅ 构建产物
│
├── docs/superpowers/specs/           # ✅ 设计文档
│   ├── 2026-05-30-admin-panel-design.md
│   └── 2026-05-30-admin-panel-plan.md (本文档)
│
├── docker-compose.yml                # ✅ 容器编排
├── Dockerfile.backend                # ✅ 后端镜像
├── Dockerfile.frontend               # ✅ 前端镜像
└── nginx.conf                        # ✅ 反向代理配置
```

### **文档交付**

- [x] 设计规范文档 (已完成)
- [x] 实施计划文档 (本文档)
- [ ] API 接口文档 (Swagger UI 自动生成)
- [ ] 部署运维手册 (上线后编写)
- [ ] 用户操作手册 (可选)

---

## ✅ 实施准备就绪

### **下一步行动**

1. **确认此实施计划** ✅ (等待用户确认)
2. **开始 Phase 1** - 环境搭建 + 认证系统
3. **每日站会** - 同步进度 + 阻塞问题
4. **每周 Review** - 阶段性成果演示

---

**文档结束** 🚀

**祝开发顺利！如有疑问请随时沟通。**
