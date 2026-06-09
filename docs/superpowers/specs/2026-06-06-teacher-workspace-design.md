# 教师工作台（Teacher Workspace）设计规格

> **日期**: 2026-06-06
> **状态**: 已批准，待实施
> **目标**: 为教师角色提供独立的班级学生管理工作台首页，替代现有通用 dashboard

---

## 1. 目标与背景

### 问题
当前教师登录后看到的是与管理员相同的通用 dashboard 和数据分析页面。这些页面展示的是**全平台聚合数据**或**个人学习数据**，不符合教师的实际需求——教师需要**以班级为单位**查看和管理自己学生的完成情况。

### 目标
- 新增独立的**教师工作台**页面 (`/teacher/workspace`)
- 教师登录后默认跳转到此页面
- 以**班级**为组织维度，展示每个学生的**完成情况、练习成绩、活跃状态**
- 提供**预警机制**自动标出需要关注的学生
- 支持**单个学生详情页**深入查看

### 不做
- 不修改管理员和学生角色的现有页面
- 不改变现有的数据分析 (analytics) 模块（保留给管理员用）
- 不做家长端/移动端适配

---

## 2. 页面路由与入口

### 新增路由

| 路径 | 组件 | 权限 | 说明 |
|------|------|------|------|
| `/teacher/workspace` | `TeacherWorkspace.vue` | teacher, admin | 教师工作台首页 |
| `/teacher/student/:id` | `StudentDetail.vue` | teacher, admin | 学生详情页 |

### 路由变更
- 教师角色登录后 **redirect 从 `/dashboard` 改为 `/teacher/workspace`**
- 侧边栏新增菜单项「我的工作台」（icon: `Monitor` 或 `DataBoard`），仅 `roles: ['admin', 'teacher']` 可见
- 原有 `/dashboard` 路由对教师仍可访问（不删除），但不再是默认首页

### URL 参数约定
- `/teacher/workspace?class_id=xxx&period=30d` — 支持带参数直接访问
- `/teacher/student/:id?period=30d` — 学生详情支持时间范围

---

## 3. 数据模型关系（现有）

```
Teacher (UserProfile, role='teacher')
  │
  ├── 管理学生 → UserProfile.objects.filter(teacher=teacher_user)
  │     │
  │     ├── .student_id        学号
  │     ├── .real_name         姓名
  │     ├── .class_info → ClassInfo   所属班级
  │     ├── .last_login        最后登录
  │     │
  │     └── 关联数据:
  │           ├── practice_records  → PracticeRecord (score, scenario, created_at)
  │           └── (学习资料通过 author 关联)
  │
  └── 管理班级 → 通过学生的 class_info 去重得到
```

---

## 4. 页面组成：教师工作台首页 (TeacherWorkspace.vue)

### 4.1 A区：顶部操作栏

```
┌─────────────────────────────────────────────────────────────┐
│  📋 我的工作台    [▼ 班级选择] [▼ 时间范围] [📥 导出报告]   │
└─────────────────────────────────────────────────────────────┘
```

**组件：**
- **班级选择器** (`el-select`)：选项来源 `GET /api/v1/auth/my_classes/`
  - 默认值：第一个班级（如果只有一个）或 "全部班级"（placeholder）
  - 切换时刷新所有数据
- **时间范围** (`el-select`)：7d / 30d / 90d / all
- **导出按钮** (`el-button`)：导出当前视图的 Excel 报告（后续迭代，首版可为 TODO）

### 4.2 B区：班级统计卡片（StatCards）

横向排列 6 个指标卡片：

| # | 指标名 | 图标 | 颜色 | 计算逻辑 |
|---|--------|------|------|---------|
| 1 | 班级人数 | User | #409EFF | 该教师管理的学生总数（受 class_id 影响） |
| 2 | 班级均分 | Star | #67C23A | 所教学生 PracticeRecord.overall_score 的 AVG |
| 3 | 资料完成率 | Reading | #E6A23C | 人均已读资料数 / 总发布资料数 × 100% |
| 4 | 活跃率 | SuccessFilled | #67C23A | 近7天有 last_login 的学生 / 总人数 × 100% |
| 5 | 练习总次数 | EditPen | #F56C6C | 所教学生 PracticeRecord 总数（受 period 影响） |
| 6 | 待关注人数 | Warning | #E6A23C | 满足预警条件的学生数量（见 E 区规则） |

每个卡片包含：图标、数值、标签、(可选)趋势箭头。

### 4.3 C区：学生总览表（StudentTable）— 核心区域

使用 `el-table` + `v-loading`，支持排序、筛选、搜索。

#### 表格列定义

| 列名 | 宽度 | 字段/计算 | 排序 | 格式 |
|------|------|----------|------|------|
| # | 50px | index | - | 序号 |
| 姓名 | 100px | `real_name` | ✅ | 文本 |
| 学号 | 120px | `student_id` | ✅ | 文本，可搜 |
| 资料完成度 | 140px | 进度条 | ✅ | `el-progress`(percentage) + 数字 |
| 练习次数 | 100px | count | ✅ 降序 | 数字 |
| 练习均分 | 100px | avg_score | ✅ 降序 | `el-tag`(颜色按分数段) |
| 最近登录 | 120px | `last_login` | ✅ | 相对时间 ("2小时前") |
| 状态 | 90px | auto | - | 🏆优秀 / ✅正常 / ⚠️需关注 |
| 操作 | 100px | - | - | `[查看详情]` 按钮 |

#### 状态判定规则（自动计算）

```python
def get_student_status(student, class_avg_score, class_avg_practices):
    avg = student.avg_score
    days_since_login = (now - student.last_login).days
    practices = student.practice_count

    if avg >= 85 and practices >= class_avg_practices:
        return 'excellent'      # 🏆 优秀
    if avg >= 60 and days_since_login <= 7:
        return 'normal'          # ✅ 正常
    return 'attention'           # ⚠️ 需关注
```

#### el-tag 颜色映射（均分）

| 分数范围 | type | 文字 |
|---------|------|------|
| ≥ 90 | success | 优秀 |
| ≥ 80 | (空) | 良好 |
| ≥ 60 | warning | 及格 |
| < 60 | danger | 不及格 |

#### 交互
- 点击 `[查看详情]` → 跳转 `/teacher/student/{user_id}`
- 支持列筛选（完成度范围、分数范围、状态）
- 支持姓名/学号搜索

### 4.4 D区：趋势分析区（Charts）

左右两栏等宽排列（`:span="12"`）：

**左栏 - 成绩分布饼图 (PieChart)：**

```
标题: 📊 班级成绩分布
数据: { excellent: N, good: N, average: N, pass: N, fail: N }
交互: 点击扇区 → 筛选 C 区表格中对应分数段的学生
```

**右栏 - 学习活跃趋势折线图 (LineChart)：**

```
标题: 📈 近30天班级活跃度
X轴: 日期
Y轴(双线):
  - 每日活跃学生数 (柱状/面积)
  - 每日练习提交次数 (折线)
```

### 4.5 E区：预警提醒区 (AlertPanel)

条件触发：仅当存在需关注学生时显示。

每条预警为一个 `el-card`（小型），包含：

```
┌──────────────────────────────────────────────────┐
│ [学生姓名]  预警原因描述                          │
│ 辅助数据（均分/登录时间等）     [查看] [通知(TODO)] │
└──────────────────────────────────────────────────┘
```

#### 预警规则（满足任一即展示）

| 规则 | 条件 | 描述文案模板 |
|------|------|-------------|
| 成绩落后 | `avg_score < class_avg_score - 10` | 「练习均分 {score}，低于班级平均 {diff} 分」 |
| 长期未登录 | `days_since_login > 7` | 「已连续 {N} 天未登录」 |
| 资料完成低 | `completion_rate < class_avg_completion * 0.5` | 「仅完成 {rate}% 学习资料（班级平均 {avg}%）」 |
| 练习不足 | `practice_count < class_avg_practices * 0.3` | 「练习次数偏少：{count}次（班级平均 {avg}次）」 |

同一学生可能触犯多条规则，合并展示最严重的 1-2 条。

### 4.6 空状态

当教师没有任何管理的学生时：
```
el-empty:
  description: "您暂未管理任何班级和学生"
  image-size: 120
  button: "联系管理员分配班级"
```

---

## 5. 学生详情页 (StudentDetail.vue)

### 5.1 布局

```
┌──────────────────────────────────────────────────────┐
│  ← 返回工作台    学生详情：{姓名} ({学号})            │
├──────────────────────┬───────────────────────────────┤
│                      │                               │
│  👤 头像 + 基本信息   │   📈 成绩趋势图                │
│  姓名、学号、班级     │   (近30天练习均分折线)         │
│  状态标签、注册时间   │                               │
│                      │                               │
│  📊 个人统计面板      │                               │
│  · 练习次数          │                               │
│  · 平均分            │                               │
│  · 最高分            │                               │
│  · 资料完成率        │                               │
│  · 活跃天数          │                               │
│                      │                               │
├──────────────────────┴───────────────────────────────┤
│  📋 练习记录明细表                                 │
│  场景 | 主题 | 得分 | 用时 | 日期                    │
└──────────────────────────────────────────────────────┘
```

### 5.2 基本信息卡

左侧卡片展示：
- 头像 (`el-avatar`, 64px)
- 姓名 (`real_name`)、学号 (`student_id`)
- 班级 (`class_info.name`)
- 状态标签（复用工作台的 🏆/✅/⚠️）
- 注册时间 (`date_joined`)

### 5.3 个人统计面板

| 指标 | 计算方式 |
|------|---------|
| 练习次数 | `PracticeRecord.filter(user=student).count()` |
| 平均分 | `AVG(overall_score)` |
| 最高分 | `MAX(overall_score)` |
| 资料完成率 | 已读资料 / 总资料（近似值） |
| 活跃天数 | 近30天内有记录的天数 |

### 5.4 成绩趋势图

- X轴：近 30 天日期
- Y轴：每日练习均分
- 标注最高/最低点

### 5.5 练习记录明细表

| 列 | 字段 | 说明 |
|----|------|------|
| 场景 | `scenario.title` | 练习场景名称 |
| 主题 | `topic.title` | 知识点主题 |
| 得分 | `overall_score` | 带颜色 tag |
| 耗时 | (如有) | 分钟 |
| 日期 | `created_at` | YYYY-MM-DD |

支持按时间范围筛选（继承 URL 的 `period` 参数）。

---

## 6. 后端 API 设计

### 6.1 工作台概览接口

```
GET /api/v1/teacher/workspace/
Auth: Bearer <token>
Params: class_id?, period?=30d

Response:
{
  "code": 200,
  "data": {
    // B区统计卡片
    "stats": {
      "total_students": 42,
      "class_avg_score": 78.5,
      "material_completion_rate": 65,
      "active_rate": 82,
      "total_practices": 520,
      "attention_count": 3
    },

    // C区学生列表
    "students": [
      {
        "id": 1,
        "real_name": "张三",
        "student_id": "202301",
        "class_name": "计算机2301",
        "completion_rate": 85,
        "practice_count": 12,
        "avg_score": 82.0,
        "last_login": "2026-06-05T14:30:00",
        "status": "excellent"  // excellent | normal | attention
      },
      ...
    ],

    // D区图表数据
    "charts": {
      "score_distribution": {
        "excellent": 5, "good": 15, "average": 12, "pass": 7, "fail": 3
      },
      "activity_trend": [
        {"date": "2026-05-07", "active_students": 28, "practice_count": 15},
        ...
      ]
    },

    // E区预警列表
    "alerts": [
      {
        "student_id": 1,
        "student_name": "李四",
        "reason": "score_low",
        "detail": "练习均分 45分，低于班级平均 33.5 分",
        "avg_score": 45,
        "last_login": "2026-06-01"
      },
      ...
    ]
  }
}
```

### 6.2 学生详情接口

```
GET /api/v1/teacher/student/<pk>/
Auth: Bearer <token>
Params: period?=30d

Response:
{
  "code": 200,
  "data": {
    "basic": {
      "id": 1, "real_name": "张三", "student_id": "202301",
      "class_name": "计算机2301", "avatar": null,
      "status": "excellent", "date_joined": "2024-09-01"
    },
    "stats": {
      "practice_count": 12, "avg_score": 82.0, "max_score": 95,
      "completion_rate": 85, "active_days": 18
    },
    "score_trend": [
      {"date": "2026-05-08", "avg_score": 78},
      ...
    ],
    "practice_records": [
      {"scenario_title": "基础语法", "topic_title": "变量",
       "overall_score": 92, "created_at": "2026-06-01"},
      ...
    ]
  }
}
```

### 6.3 权限控制

- 两个接口都需要 `IsAuthenticated`
- 仅 `role in ['admin', 'teacher']` 可访问
- 教师只能查询 `teacher=self` 的学生数据
- 管理员可查任意学生（传 `user_id` 参数）

---

## 7. 前端组件结构

```
admin-panel/src/views/teacher/
├── Workspace.vue          # 工作台首页（主文件）
└── StudentDetail.vue      # 学生详情页

admin-panel/src/api/
└── teacher.js             # 新增：教师工作台 API 调用
  - getWorkspaceData(params)
  - getStudentDetail(id, params)
```

### 复用的已有组件
- `@/components/charts/LineChart.vue`
- `@/components/charts/PieChart.vue`
- `@/components/charts/BarChart.vue`
- Element Plus 全套组件

---

## 8. 实施要点

### 后端新增文件
- `teachers/api/views.py` — TeacherWorkspaceViewSet（含 workspace + student_detail 两个 action）
- `teachers/api/urls.py` — 路由注册

### 后端修改文件
- `admin-panel/src/router/index.js` — 新增路由 + 教师默认 redirect
- `admin-panel/src/api/` — 新增 `teacher.js`

### 前端新增文件
- `admin-panel/src/views/teacher/Workspace.vue`
- `admin-panel/src/views/teacher/StudentDetail.vue`

### 前端修改文件
- 侧边栏导航配置（新增"我的工作台"菜单项）

### 不修改的文件
- 现有 analytics 模块（保留给管理员）
- 现有 dashboard（保留给学生和其他角色）
- 用户模型和数据库迁移（无需 schema 变更）

---

## 9. 验收标准

| # | 验证项 | 方法 |
|---|--------|------|
| 1 | 教师登录后默认进入工作台页面 | 登录后检查 redirect |
| 2 | 班级选择器正确加载并切换数据 | 选择不同班级验证数据变化 |
| 3 | 学生表格展示正确的完成度和成绩 | 对比数据库实际值 |
| 4 | 状态标签（优秀/正常/关注）判定正确 | 手动验证边界值 |
| 5 | 预警区正确展示需关注学生 | 构造触发条件验证 |
| 6 | 点击学生跳转详情页且数据正确 | 点击行内按钮验证 |
| 7 | 图表正确渲染 | 视觉检查饼图和折线图 |
| 8 | 管理员访问不受影响 | 管理员登录验证原有功能 |
| 9 | 学生看不到工作台路由 | 学生登录验证 403 或隐藏 |
