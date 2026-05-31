# Phase 6: 系统通知与消息中心 - 设计文档

**日期:** 2026-05-31
**版本:** v1.0
**状态:** 待审核

---

## 1. 项目概述

### 1.1 目标

为 Prompt Teacher 教学平台构建完整的系统通知与消息中心，支持：
- **实时推送**: 基于 WebSocket 的即时通知
- **多类型通知**: 系统通知、学习任务、练习成绩、互动消息
- **混合存储策略**: 重要通知持久化 + 临时通知仅实时推送
- **全局铃铛组件**: 未读提醒、快速预览、跳转详情

### 1.2 技术选型

| 层面 | 技术方案 | 理由 |
|------|----------|------|
| 后端框架 | Django REST Framework | 与现有架构一致 |
| 实时通信 | 轻量级 WebSocket | 无需额外依赖（Redis） |
| 数据库 | SQLite/PostgreSQL | 复用现有数据库 |
| 前端框架 | Vue3 + Composition API | 与现有前端一致 |
| UI组件库 | Element Plus | 与现有UI一致 |
| 状态管理 | Pinia | 与现有状态管理一致 |

### 1.3 核心需求

#### 支持的通知类型
1. **系统通知 (system)**: 系统公告、维护通知、新功能发布
2. **学习任务 (learning)**: 作业截止提醒、课程更新、资料发布
3. **练习成绩 (practice)**: 练习结果、成绩达标、进度警告
4. **互动消息 (interaction)**: @提及、评论回复、用户间消息

#### 推送方式
- **WebSocket 实时推送**: 用户在线时即时收到
- **数据库持久化**: 重要通知保存到历史记录
- **混合模式**: 根据通知重要性选择存储策略

#### 前端展示
- **全局通知铃铛**: 右上角显示未读数量，点击展开下拉列表
- **消息中心页面**: 完整列表展示，支持筛选、搜索、批量操作

---

## 2. 系统架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        前端 (Vue3)                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Notification │  │   Message    │  │   Notification       │  │
│  │   Bell 组件   │  │  Center 页面 │  │   WebSocket Client   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
│         ▼                 ▼                      ▼              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Pinia Store (notification)               │   │
│  │  - unreadCount: number                                   │   │
│  │  - notifications: array                                  │   │
│  │  - wsConnection: WebSocket                               │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    HTTP/WebSocket
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     后端 (Django)                                │
│                                                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐   │
│  │  REST API      │  │  WebSocket     │  │ Notification    │   │
│  │  (ViewSet)     │  │  Endpoint      │  │ Service         │   │
│  └────────┬───────┘  └───────┬────────┘  └────────┬────────┘   │
│           └──────────────────┼─────────────────────┘            │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   Models (notifications)                │    │
│  │  - Notification (通知主表)                              │    │
│  │  - NotificationTemplate (通知模板)                       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Signal Handlers (触发器)                    │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 核心组件职责

| 组件 | 职责 | 技术栈 |
|------|------|--------|
| **Notification Bell** | 全局铃铛，显示未读数，下拉预览 | Vue3 + Element Plus |
| **Message Center** | 消息列表页，支持筛选、搜索、批量操作 | Vue3 + Element Plus Table |
| **WebSocket Client** | 实时连接管理、消息接收、自动重连 | 原生 WebSocket API |
| **Pinia Store** | 状态管理：未读数、通知列表、连接状态 | Pinia |
| **REST API** | CRUD操作、标记已读、历史查询 | Django DRF ViewSet |
| **WebSocket Endpoint** | WS连接、消息推送、心跳检测 | Django自定义View |
| **Notification Service** | 业务逻辑封装、发送策略、模板渲染 | Python Service类 |
| **Models** | 数据持久化、状态管理 | Django ORM |
| **Signal Handlers** | 事件监听、自动触发通知发送 | Django Signals |

### 2.3 数据流示意

```
[触发事件] → [Signal Handler]
    → [Notification Service.create()]
        → [保存到数据库] (重要通知)
        → [WebSocket broadcast()] (实时推送)
            → [前端 WebSocket 接收]
                → [更新 Pinia Store]
                    → [UI 更新: 铃铛未读数+1 / Toast提示]

[用户操作] → [点击铃铛]
    → [调用 REST API 获取最新通知]
        → [显示下拉列表]

[用户操作] → [点击"标记已读"]
    → [REST API mark_read()]
        → [数据库更新 is_read=True]
        → [返回成功 → UI更新]
```

---

## 3. 数据模型设计

### 3.1 Notification 模型（通知主表）

```python
class Notification(models.Model):
    """通知主表 - 存储所有持久化通知"""

    NOTIFICATION_TYPES = [
        ('system', '系统通知'),
        ('learning', '学习任务'),
        ('practice', '练习成绩'),
        ('interaction', '互动消息'),
        ('announcement', '公告'),
    ]

    PRIORITY_LEVELS = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('urgent', '紧急'),
    ]

    id = models.BigAutoField(primary_key=True)

    # 基本信息
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        db_index=True,
        verbose_name='通知类型'
    )

    title = models.CharField(
        max_length=200,
        verbose_name='通知标题'
    )

    content = models.TextField(
        verbose_name='通知内容',
        help_text='支持HTML格式'
    )

    # 接收者
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='接收用户'
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
        verbose_name='发送者'
    )

    # 优先级和状态
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default='medium',
        db_index=True,
        verbose_name='优先级'
    )

    is_read = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name='是否已读'
    )

    is_persistent = models.BooleanField(
        default=True,
        verbose_name='是否持久化',
        help_text='True: 保存到数据库; False: 仅实时推送'
    )

    # 关联数据
    link = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='跳转链接',
        help_text='点击通知后跳转的页面'
    )

    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='关联对象ID',
        help_text='关联的学习资料/练习记录等'
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='关联对象类型'
    )

    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='创建时间'
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='阅读时间'
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='过期时间',
        help_text='过期后自动标记已读并归档'
    )

    # 元数据
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='元数据',
        help_text='存储额外信息，如图标、颜色等'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', '-created_at']),
            models.Index(fields=['recipient', 'notification_type', '-created_at']),
            models.Index(fields=['recipient', 'priority', 'is_read']),
        ]
        verbose_name = '通知'
        verbose_name_plural = '通知列表'
```

### 3.2 NotificationTemplate 模型（通知模板）

```python
class NotificationTemplate(models.Model):
    """通知模板 - 预定义的通知格式"""

    TEMPLATE_TYPES = [
        ('practice_completed', '练习完成'),
        ('practice_score_high', '成绩优秀'),
        ('practice_score_low', '成绩警告'),
        ('material_published', '资料发布'),
        ('assignment_due', '作业即将到期'),
        ('assignment_overdue', '作业已逾期'),
        ('system_maintenance', '系统维护'),
        ('new_feature', '新功能发布'),
        ('mentioned', '被@提及'),
        ('comment_replied', '评论回复'),
    ]

    id = models.BigAutoField(primary_key=True)

    template_code = models.CharField(
        max_length=50,
        unique=True,
        choices=[(t[0], t[1]) for t in TEMPLATE_TYPES],
        verbose_name='模板代码'
    )

    title_template = models.CharField(
        max_length=200,
        verbose_name='标题模板',
        help_text='使用 {variable} 占位符'
    )

    content_template = models.TextField(
        verbose_name='内容模板',
        help_text='支持 {variable} 和 HTML'
    )

    notification_type = models.CharField(
        max_length=20,
        choices=Notification.NOTIFICATION_TYPES,
        verbose_name='通知类型'
    )

    priority = models.CharField(
        max_length=10,
        choices=Notification.PRIORITY_LEVELS,
        default='medium',
        verbose_name='默认优先级'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用'
    )

    is_persistent = models.BooleanField(
        default=True,
        verbose_name='是否持久化'
    )

    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='图标',
        help_text='Element Plus 图标名称或emoji'
    )

    link_pattern = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='链接模式',
        help_text='使用 {id} 等占位符生成链接'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def render(self, context: dict) -> dict:
        """
        渲染模板，返回标题和内容

        Args:
            context: 变量字典，如 {'username': '张三', 'score': 95}

        Returns:
            {'title': '...', 'content': '...', ...}
        """
        title = self.title_template.format(**context)
        content = self.content_template.format(**context)

        link = ''
        if self.link_pattern:
            try:
                link = self.link_pattern.format(**context)
            except KeyError:
                link = ''

        return {
            'title': title,
            'content': content,
            'link': link,
            'icon': self.icon,
            'notification_type': self.notification_type,
            'priority': self.priority,
            'is_persistent': self.is_persistent
        }

    class Meta:
        verbose_name = '通知模板'
        verbose_name_plural = '通知模板'
```

### 3.3 数据库关系图

```
┌─────────────────────┐       ┌──────────────────────────┐
│   UserProfile       │       │    NotificationTemplate  │
│─────────────────────│       │──────────────────────────│
│ PK: id              │◄──────│ FK: (无直接关联)          │
│     username        │       │ PK: id                   │
│     role            │       │     template_code (UNIQUE)│
│                     │       │     title_template        │
└─────────────────────┘       │     content_template      │
        │                    │     notification_type      │
        │ 1:N                │     priority               │
        ▼                    └──────────────────────────┘
┌─────────────────────────────────────────────┐
│              Notification                    │
│─────────────────────────────────────────────│
│ PK: id                                      │
│ FK: recipient → UserProfile                 │
│ FK: sender → UserProfile (nullable)         │
│     notification_type (indexed)             │
│     title                                   │
│     content                                 │
│     priority (indexed)                      │
│     is_read (indexed)                       │
│     is_persistent                           │
│     link                                    │
│ FK: content_type → ContentType (generic)    │
│     object_id                               │
│     created_at (indexed)                    │
│     read_at                                 │
│     expires_at                              │
│     metadata (JSONField)                    │
└─────────────────────────────────────────────┘
```

---

## 4. API与接口设计

### 4.1 RESTful API 接口

**基础路径：** `/api/v1/notifications/`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/` | 获取通知列表（分页、筛选） | 已登录用户 |
| GET | `/{id}/` | 获取通知详情 | 接收者本人 |
| PUT | `/{id}/read/` | 标记单条已读 | 接收者本人 |
| POST | `/read-all/` | 批量标记全部已读 | 已登录用户 |
| DELETE | `/{id}/` | 删除通知 | 接收者本人/管理员 |
| GET | `/unread-count/` | 获取未读数量 | 已登录用户 |
| POST | `/send/` | 发送通知（管理员） | admin/teacher |

#### 4.1.1 请求/响应示例

**GET /api/v1/notifications/** (获取列表)
```json
// Query Parameters
{
  "page": 1,
  "page_size": 20,
  "notification_type": "",
  "is_read": null,
  "priority": "",
  "search": ""
}

// Response
{
  "code": 200,
  "message": "获取通知列表成功",
  "data": {
    "count": 150,
    "total_pages": 8,
    "current_page": 1,
    "results": [...],
    "unread_count": 12
  }
}
```

**POST /api/v1/notifications/send/** (发送通知)
```json
// Request Body
{
  "recipient_id": 5,
  "template_code": "practice_completed",
  "context": {"score": 85, "scenario_name": "提示词基础"},
  "priority": "medium",
  "link": "/admin/practice/records?id=456"
}

// Response
{
  "code": 201,
  "message": "通知发送成功",
  "data": {
    "sent_count": 1,
    "notification_ids": [123]
  }
}
```

### 4.2 WebSocket 接口设计

**连接地址：** `ws://localhost:8000/ws/notifications/?token={access_token}`

#### 4.2.1 连接认证流程

```
客户端建立连接 → 携带JWT Token → 服务端验证Token → 加入用户组 → 发送确认消息
```

#### 4.2.2 消息格式规范

**服务器 → 客户端 (Server Push):**
```typescript
interface ServerMessage {
  type: 'new_notification' | 'heartbeat' | 'unread_count_update';
  payload?: NotificationPayload;
  timestamp: string;
}

interface NewNotificationPayload {
  id: number;
  notification_type: string;
  title: string;
  content: string;
  priority: string;
  link?: string;
  metadata: { icon: string; color?: string };
  created_at: string;
}
```

**客户端 → 服务器 (Client Send):**
```typescript
interface ClientMessage {
  type: 'ping' | 'mark_read' | 'get_unread_count';
  payload?: { notification_id?: number };
}
```

#### 4.2.3 心跳机制

- **频率**: 每30秒一次
- **客户端发送**: `{ type: 'ping' }`
- **服务端响应**: `{ type: 'heartbeat', payload: { server_time: '...' } }`
- **超时检测**: 如果60秒内未收到心跳响应，断开重连

---

## 5. 前端组件设计

### 5.1 组件架构

```
App.vue
 └── NotificationBell.vue (全局组件)
      ├── 铃铛图标 + 未读徽章
      └── NotificationDropdown.vue
           ├── Tab切换 (4种类型)
           ├── 通知列表 (最近5-10条)
           └── 底部操作栏 (查看全部/全部已读)

MessageCenter.vue (独立页面)
 ├── 页面标题 + 未读统计
 ├── 筛选栏 (类型/状态/优先级/搜索)
 ├── 工具栏 (全选/批量操作)
 ├── 通知表格 (el-table)
 └── 分页器 (el-pagination)
```

### 5.2 核心组件说明

#### 5.2.1 NotificationBell.vue (全局铃铛)

**功能特性：**
- 显示未读通知数量（实时更新）
- 点击展开下拉菜单
- Tab 切换不同类型通知
- 快捷操作：查看全部、全部已读
- 新消息到达时的动画效果

**Props:**
```typescript
interface Props {
  maxCount?: number;    // 最大显示数字 (默认: 99)
  showDot?: boolean;    // 仅显示红点 (默认: false)
}
```

#### 5.2.2 MessageCenter.vue (消息中心)

**功能特性：**
- 完整的通知列表展示
- 高级筛选（类型、状态、优先级、时间范围）
- 搜索功能（标题+内容）
- 批量操作（删除、标记已读）
- 分页加载
- 点击跳转到关联页面

**筛选参数：**
```typescript
interface Filters {
  type: string;         // 通知类型
  isRead: boolean|null; // 阅读状态
  priority: string;     // 优先级
  search: string;       // 搜索关键词
  dateRange: [Date, Date]; // 时间范围
}
```

### 5.3 状态管理 (Pinia Store)

```typescript
// store/modules/notification.ts

export const useNotificationStore = defineStore('notification', () => {
  // State
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const isLoading = ref(false)

  // Getters
  const unreadNotifications = computed(() =>
    notifications.value.filter(n => !n.is_read)
  )

  // Actions
  async function fetchNotifications(params?) { ... }
  async function fetchUnreadCount() { ... }
  async function markAsRead(id: number) { ... }
  async function markAllAsRead() { ... }
  async function deleteNotification(id: number) { ... }
  function addNotification(notification) { ... }  // WebSocket调用

  return {
    notifications, unreadCount, isLoading,
    unreadNotifications,
    fetchNotifications, fetchUnreadCount,
    markAsRead, markAllAsRead, deleteNotification,
    addNotification
  }
})
```

### 5.4 WebSocket Composable

```typescript
// composables/useWebSocket.ts

export function useWebSocket() {
  let ws: WebSocket | null = null

  function connect() {
    const token = useAuthStore().token
    ws = new WebSocket(`ws://localhost:8000/ws/notifications/?token=${token}`)

    ws.onopen = () => { /* 启动心跳 */ }
    ws.onmessage = (event) => { /* 处理消息 */ }
    ws.onclose = () => { /* 自动重连 */ }
  }

  function sendMessage(message: ClientMessage) { ... }
  function disconnect() { ... }

  return { isConnected, connect, disconnect, sendMessage }
}
```

---

## 6. 业务集成场景

### 6.1 自动触发的通知场景

#### 场景1: 练习完成通知

**触发时机:** PracticeRecord 创建时

**实现方式:** Django Signal (post_save)

**通知内容示例:**
```
标题: 🎉 练习完成！得分: 85分
内容: 您完成了"提示词基础"场景的练习，获得85分评价。
类型: practice
优先级: medium (>=90: high, <60: urgent)
```

#### 场景2: 学习资料发布通知

**触发时机:** LearningMaterial 状态变为 published

**实现方式:** Django Signal (post_save)

**目标用户:** 所有学生

**通知内容示例:**
```
标题: 📚 新学习资料发布
内容: 教师 张老师 发布了新资料《Prompt Engineering进阶》
类型: learning
优先级: medium
```

#### 场景3: 系统公告

**触发时机:** 管理员手动发布

**实现方式:** Admin API 调用

**目标用户:** 所有用户 或 指定角色

**通知内容示例:**
```
标题: 🔧 系统维护通知
内容: 系统将于今晚22:00-23:00进行升级维护，届时将暂停服务...
类型: announcement
优先级: high
```

### 6.2 NotificationService 核心方法

```python
class NotificationService:

    @classmethod
    def send_to_user(cls, user, template_code=None, context=None, **kwargs):
        """
        向单个用户发送通知
        - 使用模板渲染 或 直接指定内容
        - 保存到数据库 (如果 is_persistent=True)
        - 通过 WebSocket 实时推送
        """

    @classmethod
    def broadcast(cls, recipients: List, **kwargs):
        """向多个用户批量发送"""

    @classmethod
    def _push_to_user(cls, user, payload: dict):
        """通过 WebSocket 推送消息"""
```

---

## 7. 实施计划

### 7.1 分阶段实施

| 阶段 | 任务 | 预计时间 | 交付物 |
|------|------|----------|--------|
| **Phase 6.1** | 基础设施搭建 | 0.5天 | App、Models、Migrations |
| **Phase 6.2** | REST API开发 | 0.5天 | ViewSet、Serializers、URLs |
| **Phase 6.3** | WebSocket实现 | 1天 | WS Endpoint、连接管理 |
| **Phase 6.4** | 前端组件开发 | 1天 | Bell、MessageCenter、Store |
| **Phase 6.5** | 集成与测试 | 0.5天 | Signals、测试、联调 |

**总计: 约3.5天**

### 7.2 详细任务清单

#### Phase 6.1: 基础设施搭建 (2-3小时)

- [ ] 创建 `notifications` Django App
- [ ] 添加到 `INSTALLED_APPS`
- [ ] 实现 `Notification` 模型
- [ ] 实现 `NotificationTemplate` 模型
- [ ] 运行 `makemigrations && migrate`
- [ ] 创建服务层文件结构

#### Phase 6.2: REST API开发 (2-3小时)

- [ ] 实现 `NotificationSerializer`
- [ ] 实现 `SendNotificationSerializer`
- [ ] 实现 `NotificationViewSet`
  - [ ] list() - 列表查询
  - [ ] retrieve() - 详情
  - [ ] mark_read() - 标记已读
  - [ ] mark_all_read() - 全部已读
  - [ ] destroy() - 删除
  - [ ] unread_count() - 未读数
  - [ ] send() - 发送通知
- [ ] 配置 URL 路由

#### Phase 6.3: WebSocket实现 (4-5小时)

- [ ] 实现 `NotificationWebSocketView`
  - [ ] connect() - 连接认证
  - [ ] receive() - 接收消息
  - [ ] disconnect() - 断开处理
  - [ ] notify() - 推送消息
- [ ] 配置 ASGI 支持
- [ ] 实现心跳机制
- [ ] 实现连接管理和重连

#### Phase 6.4: 前端组件开发 (4-5小时)

- [ ] 实现 Pinia Store (`store/modules/notification.ts`)
- [ ] 封装 API (`src/api/notification.js`)
- [ ] 开发 `NotificationBell.vue` 组件
- [ ] 开发 `MessageCenter.vue` 页面
- [ ] 实现 `useWebSocket` Composable
- [ ] 集成到 `AdminLayout.vue`
- [ ] 配置路由

#### Phase 6.5: 集成与测试 (2-3小时)

- [ ] 实现 Signal Handlers
  - [ ] on_practice_completed()
  - [ ] on_material_published()
  - [ ] 其他业务场景
- [ ] 初始化通知模板数据
- [ ] 编写单元测试
- [ ] 前后端联调测试
- [ ] 多角色权限测试
- [ ] 性能优化

---

## 8. 关键技术要点

### 8.1 并发安全

```python
# 标记已读使用 select_for_update 避免竞态条件
@transaction.atomic
def mark_as_read_safe(notification_id, user_id):
    notification = Notification.objects.select_for_update().get(
        id=notification_id,
        recipient_id=user_id
    )
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save(update_fields=['is_read', 'read_at'])
    return notification
```

### 8.2 批量操作优化

```python
# 批量插入优化 (避免N+1问题)
def batch_create_notifications(notifications_data: List[dict]):
    notifications = [Notification(**data) for data in notifications_data]
    return Notification.objects.bulk_create(notifications, batch_size=100)
```

### 8.3 过期通知清理

```python
# 定时任务清理过期通知
class Command(BaseCommand):
    def handle(self, *args, **options):
        expired = Notification.objects.filter(
            expires_at__lt=timezone.now(),
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
```

### 8.4 存储策略决策

```python
# 重要通知: 同时使用数据库和WebSocket确保可靠
if is_persistent:
    save_to_database()      # 保证不丢失
    push_via_websocket()    # 实时体验

# 临时通知: 仅WebSocket
if not is_persistent:
    push_via_websocket()    # 用户在线才收到
```

---

## 9. 测试计划

### 9.1 单元测试

- [ ] Model 测试 (CRUD、字段验证)
- [ ] Serializer 测试 (序列化/反序列化)
- [ ] Service 层测试 (发送逻辑、模板渲染)
- [ ] Signal Handler 测试 (触发条件)

### 9.2 集成测试

- [ ] API 接口测试 (所有端点)
- [ ] WebSocket 连接测试 (认证、消息收发)
- [ ] 权限控制测试 (多角色访问)
- [ ] 并发安全性测试

### 9.3 E2E 测试

- [ ] 完整通知流程 (触发→发送→接收→展示→已读)
- [ ] 多用户并发通知
- [ ] 离线消息恢复
- [ ] 大批量通知性能

---

## 10. 未来扩展方向

### 10.1 可能的增强功能

1. **邮件通知**: 对重要通知增加邮件备份
2. **短信通知**: 紧急通知通过短信发送
3. **通知偏好设置**: 用户自定义接收哪些类型通知
4. **定时通知**: 定时发送提醒（如作业到期前1天）
5. **通知聚合**: 相似通知合并展示
6. **已读同步**: 多设备间已读状态同步

### 10.2 架构升级路径

当前方案 → 升级到 Django Channels (当需要以下功能时):
- 需要房间/群组概念
- 并发用户超过1000人
- 需要更复杂的消息路由
- 需要消息持久化和离线恢复

---

## 附录

### A. 通知模板初始数据

系统应预置以下通知模板：

| 模板代码 | 名称 | 类型 | 优先级 | 持久化 |
|---------|------|------|--------|--------|
| practice_completed | 练习完成 | practice | medium | ✅ |
| practice_score_high | 成绩优秀 | practice | high | ✅ |
| practice_score_low | 成绩警告 | practice | urgent | ✅ |
| material_published | 资料发布 | learning | medium | ✅ |
| assignment_due | 作业即将到期 | learning | high | ✅ |
| assignment_overdue | 作业已逾期 | learning | urgent | ✅ |
| system_maintenance | 系统维护 | system | high | ✅ |
| new_feature | 新功能发布 | system | low | ✅ |
| mentioned | 被@提及 | interaction | medium | ❌ |
| comment_replied | 评论回复 | interaction | low | ❌ |

### B. 错误码定义

| 错误码 | 说明 | HTTP状态码 |
|-------|------|-----------|
| 40001 | Token无效或过期 | 401 |
| 40002 | 无权限发送通知 | 403 |
| 40003 | 通知不存在 | 404 |
| 40004 | 参数验证失败 | 422 |
| 50001 | WebSocket连接失败 | 500 |
| 50002 | 模板渲染错误 | 500 |

### C. 环境变量配置

```bash
# .env
VITE_WS_BASE_URL=ws://localhost:8000
NOTIFICATION_HEARTBEAT_INTERVAL=30  # 秒
NOTIFICATION_RECONNECT_DELAY=5000  # 毫秒
NOTIFICATION_MAX_RECONNECT_ATTEMPTS=10
```

---

**文档结束**

*请审阅此设计文档，如有任何疑问或建议请反馈。*
