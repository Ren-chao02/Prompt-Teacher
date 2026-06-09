# 教师数据分析 - 基于班级数据过滤 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将教师的数据分析界面从"全平台数据"改为"仅显示自己管理班级的学生数据"

**Architecture:** 后端通过 `UserProfile.teacher` FK 关系（学生→教师）间接获取教师管理的学生集合，在 analytics 视图层按此集合过滤 QuerySet；前端增加班级选择器，传递 `class_id` 参数给后端。

**Tech Stack:** Django DRF + Vue3 + Element Plus + Pinia

**当前数据模型关系:**
```
ClassInfo (班级)
  └── UserProfile.class_info → 学生所属班级

UserProfile (用户)
  ├── student.teacher → 学生的指导教师 (FK→self, role=teacher)
  └── student.class_info → 学生所属班级 (FK→ClassInfo)

教师管理范围 = teacher字段指向该教师的所有学生 → 这些学生所属的班级
```

---

## 影响范围全景图

```
┌─────────────────────────────────────────────────────────────────┐
│                        需要修改的文件                              │
├──────────────┬──────────────────────────┬───────────────────────┤
│   层级       │         文件              │      修改内容          │
├──────────────┼──────────────────────────┼───────────────────────┤
│ 后端-服务层  │ analytics/services/       │ 实现 filter_by_role   │
│              │   base_analytics.py       │ 的教师班级过滤 TODO    │
├──────────────┼──────────────────────────┼───────────────────────┤
│ 后端-API层   │ analytics/api/views.py    │ 3个接口全部加教师过滤   │
│              │                          │ overview /             │
│              │                          │ learning_progress /    │
│              │                          │ practice_statistics     │
├──────────────┼──────────────────────────┼───────────────────────┤
│ 后端-API层   │ users/api/views.py       │ 新增"我的班级"接口      │
│              │                          │ (返回教师管理的班级列表) │
├──────────────┼──────────────────────────┼───────────────────────┤
│ 前端-API层   │ admin-panel/src/api/      │ 新增 getMyClasses()   │
│              │   auth.js 或 analytics.js │ analytics API 加参数   │
├──────────────┼──────────────────────────┼───────────────────────┤
│ 前端-页面    │ views/analytics/          │ 3个页面都加班级选择器   │
│              │   Overview.vue            │ 标题改为"我的班级数据"  │
│              │   PracticeStatistics.vue  │                      │
│              │   LearningProgress.vue    │                      │
└──────────────┴──────────────────────────┴───────────────────────┘
```

---

### Task 1: 后端 - 实现教师班级过滤核心逻辑

**Files:**
- Modify: `analytics/services/base_analytics.py` (第85-95行 `filter_by_role` 方法)
- Modify: `analytics/api/views.py` (AnalyticsViewSet 类)

- [ ] **Step 1: 在 base_analytics.py 中实现教师班级过滤**

修改 `filter_by_role()` 方法中 `role == 'teacher'` 分支，将 TODO 替换为实际实现：

```python
# 文件: analytics/services/base_analytics.py
# 位置: filter_by_role() 方法, elif role == 'teacher' 分支

elif role == 'teacher':
    # 教师只能看到自己管理的学生数据
    from users.models import UserProfile
    
    # 获取该教师管理的所有学生ID
    managed_student_ids = UserProfile.objects.filter(
        teacher=user
    ).values_list('pk', flat=True)
    
    if not managed_student_ids:
        return queryset.none()
    
    # 根据 queryset 模型类型决定如何过滤
    model = queryset.model
    
    # PracticeRecord 等有 user 字段的模型
    if hasattr(model, 'user') or hasattr(model, 'user_id'):
        return queryset.filter(user_id__in=managed_student_ids)
    
    # UserProfile 模型
    if model == UserProfile:
        return queryset.filter(pk__in=managed_student_ids)
    
    # 其他模型：尝试 user 外键
    try:
        return queryset.filter(user_id__in=managed_student_ids)
    except Exception:
        return queryset
```

同时新增一个辅助方法，供视图层直接使用：

```python
@classmethod
def get_teacher_managed_student_ids(cls, teacher_user):
    """获取教师管理的学生ID列表"""
    from users.models import UserProfile
    return list(UserProfile.objects.filter(
        teacher=teacher_user
    ).values_list('pk', flat=True))

@classmethod
def get_teacher_managed_class_ids(cls, teacher_user):
    """获取教师管理的班级ID列表（通过学生关联）"""
    from users.models import UserProfile
    return list(UserProfile.objects.filter(
        teacher=teacher_user
    ).exclude(class_info=None).values_list(
        'class_id', flat=True
    ).distinct())
```

- [ ] **Step 2: 验证 base_analytics 修改**

运行测试确认无语法错误：
```bash
cd "/home/mjl/Prompt Teacher" && python -c "from analytics.services.base_analytics import BaseAnalyticsService; print('OK')"
```

预期输出: `OK`

---

### Task 2: 后端 - 修改 AnalyticsViewSet 的 3 个接口

**Files:**
- Modify: `analytics/api/views.py`

#### 2.1 overview 接口

- [ ] **Step 1: 修改 overview() 方法**

在 `overview()` 方法开头（约第55行之后），添加教师数据过滤：

```python
@action(detail=False, methods=['get'])
def overview(self, request):
    user = request.user
    period = request.query_params.get('period', '30d')
    start_date, end_date = BaseAnalyticsService.get_time_range(period)
    
    # ===== 新增: 教师权限过滤 =====
    role = getattr(user, 'role', 'student')
    teacher_student_ids = None
    if role == 'teacher':
        teacher_student_ids = BaseAnalyticsService.get_teacher_managed_student_ids(user)
        if not teacher_student_ids:
            # 教师没有管理任何学生，返回空数据
            return Response({
                'code': 200,
                'message': '您暂未管理任何学生',
                'data': {
                    'learning': {'total_materials': 0, 'today_new': 0, 'completion_rate': 0, 'avg_read_time': 0},
                    'practice': {'total_records': 0, 'avg_score': 0, 'pass_rate': 0},
                    'users': {'active_today': 0, 'new_this_week': 0, 'retention_rate': 0},
                    'daily_trend': [],
                    'top_content': [],
                    'top_users': []
                }
            })
    # ===== 结束新增 =====
    
    data = {
        'learning': self._get_learning_overview(start_date, end_date),
        'practice': self._get_practice_overview(start_date, end_date, teacher_student_ids),
        'users': self._get_user_overview(start_date, end_date, teacher_student_ids),
        ...
    }
```

- [ ] **Step 2: 修改 _get_practice_overview() 方法签名和实现**

```python
def _get_practice_overview(self, start_date=None, end_date=None, student_ids=None):
    """获取练习模块概览数据"""
    base_qs = PracticeRecord.objects.all()
    
    # 新增：教师过滤
    if student_ids:
        base_qs = base_qs.filter(user_id__in=student_ids)
    
    if start_date and end_date:
        base_qs = base_qs.filter(created_at__range=[start_date, end_date])
    
    ... # 其余不变
```

- [ ] **Step 3: 修改 _get_top_users() 方法**

```python
def _get_top_users(self, limit=10, student_ids=None):
    """获取优秀学员排行"""
    qs = UserProfile.objects.annotate(...)
    
    # 新增：教师过滤
    if student_ids:
        qs = qs.filter(pk__in=student_ids)
    
    ...
```

- [ ] **Step 4: 修改 _get_daily_trend() 方法**

```python
def _get_daily_trend(self, start_date=None, end_date=None, student_ids=None):
    # 练习记录部分需要过滤
    practice_count = PracticeRecord.objects.filter(...)
    if student_ids:
        practice_count = practice_count.filter(user_id__in=student_ids)
    ...
```

#### 2.2 practice_statistics 接口

- [ ] **Step 5: 修改 practice_statistics() 方法**

在方法内添加教师过滤，影响以下子方法调用：

```python
@action(detail=False, methods=['get'])
def practice_statistics(self, request):
    user = request.user
    ...
    
    # ===== 新增 =====
    role = getattr(user, 'role', '')
    teacher_student_ids = None
    if role == 'teacher':
        teacher_student_ids = BaseAnalyticsService.get_teacher_managed_student_ids(user)
    # ===== 结束新增 =====
    
    data = {
        'score_trend': self._get_score_trend(target_user_id, scenario_id, start_date, end_date, teacher_student_ids),
        'distribution': self._get_score_distribution(target_user_id, scenario_id, score_level, teacher_student_ids),
        'scenario_comparison': self._get_scenario_comparison(target_user_id, teacher_student_ids),
        'weak_points': self._identify_weak_points(target_user_id, teacher_student_ids)
    }
    
    # 排行榜也需过滤
    if role in ['admin', 'teacher']:
        data['ranking'] = self._get_practice_ranking(scenario_id, limit=20, student_ids=teacher_student_ids)
    ...
```

- [ ] **Step 6: 修改所有 _get_* 子方法签名**

每个接收数据的子方法都需要新增 `student_ids=None` 参数，并在查询时应用过滤：

| 方法 | 过滤位置 |
|------|----------|
| `_get_score_trend()` | `base_qs.filter(user_id__in=student_ids)` |
| `_get_score_distribution()` | `base_qs.filter(user_id__in=student_ids)` |
| `_get_scenario_comparison()` | `base_qs.filter(user_id__in=student_ids)` |
| `_identify_weak_points()` | `base_qs.filter(user_id__in=student_ids)` |
| `_get_practice_ranking()` | `.filter(pk__in=student_ids)` |

#### 2.3 learning_progress 接口

- [ ] **Step 7: 修改 learning_progress() 方法**

学习进度页面对教师的语义需调整——教师看到的是**所教学生的学习进度汇总**，而非个人进度：

```python
@action(detail=False, methods=['get'])
def learning_progress(self, request):
    user = request.user
    ...
    
    role = getattr(user, 'role', '')
    teacher_student_ids = None
    
    # 权限控制
    target_user_id = user_id
    if role == 'student':
        target_user_id = str(user.id)
    elif role == 'teacher':
        # 教师：查看所教学生的汇总学习数据
        teacher_student_ids = BaseAnalyticsService.get_teacher_managed_student_ids(user)
        if not teacher_student_ids:
            target_user_id = None  # 返回空数据
        # 不指定单个 user_id，而是传 student_ids 给各子方法
        target_user_id = None  # 教师看汇总，不看单人
    
    data = {
        'timeline': self._get_learning_timeline_for_students(teacher_student_ids, start_date, end_date),
        ...
    }
```

> **注意**: LearningProgress 对教师的展示意义需要重新定义。当前设计是基于单个用户的阅读时间线，教师场景应改为"班级学生学习活跃度时间线"。这涉及较大的语义变更，建议 Task 7 中统一处理前端展示调整。

---

### Task 3: 后端 - 新增"我的班级"API 接口

**Files:**
- Modify: `users/api/views.py`

- [ ] **Step 1: 在 UserViewSet 或新建视图中添加 my_classes 接口**

```python
# 文件: users/api/views.py
# 在适当位置（如 CurrentUserAPIView 同级或 UserViewSet 中）新增:

@action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
def my_classes(self, request):
    """
    获取当前教师管理的班级列表
    返回该教师通过学生关联的所有班级，附带每个班级的学生数量
    """
    user = request.user
    
    if getattr(user, 'role', '') not in ['admin', 'teacher']:
        return Response({'code': 403, 'message': '无权限'}, status=403)
    
    from users.models import ClassInfo
    from django.db.models import Count
    
    # 通过学生关联获取班级
    classes = ClassInfo.objects.filter(
        students__teacher=user
    ).annotate(
        student_count=Count('students')
    ).distinct().values(
        'id', 'name', 'grade', 'major', 'class_number', 'student_count'
    )
    
    return Response({
        'code': 200,
        'data': list(classes)
    })
```

- [ ] **Step 2: 注册 URL**

确认 URL 路由已注册（通常在 `users/api/urls.py` 中）。

---

### Task 4: 前端 - 新增 API 调用

**Files:**
- Modify: `admin-panel/src/api/analytics.js`
- Modify: `admin-panel/src/api/auth.js` (或新建 class.js)

- [ ] **Step 1: analytics.js 所有接口增加 class_id 参数**

```javascript
// admin-panel/src/api/analytics.js

export function getAnalyticsOverview(params = {}) {
  return request({
    url: '/analytics/overview/',
    method: 'get',
    params: { period: '30d', ...params }  // params 可包含 class_id
  })
}

export function getLearningProgress(params = {}) {
  return request({
    url: '/analytics/learning_progress/',
    method: 'get',
    params: { period: '30d', ...params }
  })
}

export function getPracticeStatistics(params = {}) {
  return request({
    url: '/analytics/practice_statistics/',
    method: 'get',
    params: { period: '30d', ...params }
  })
}
```

- [ ] **Step 2: 新增 getMyClasses 接口**

```javascript
// admin-panel/src/api/auth.js (末尾追加)

/**
 * 获取教师管理的班级列表
 */
export function getMyClasses() {
  return request({
    url: '/auth/my_classes/',
    method: 'get'
  })
}
```

---

### Task 5: 前端 - Overview.vue 改造

**Files:**
- Modify: `admin-panel/src/views/analytics/Overview.vue`

- [ ] **Step 1: 添加班级选择器和状态**

在 `<template>` 的 `<page-header>` 区域，period 选择器旁边添加班级选择器：

```html
<!-- 仅教师显示班级选择器 -->
<el-select 
  v-if="isTeacher && myClasses.length > 0" 
  v-model="selectedClassId" 
  placeholder="选择班级" 
  clearable 
  style="width: 180px; margin-left: 10px;"
>
  <el-option 
    v-for="cls in myClasses" 
    :key="cls.id" 
    :label="`${cls.name} (${cls.student_count}人)`" 
    :value="cls.id" 
  />
</el-select>
```

- [ ] **Step 2: 添加 script 逻辑**

```javascript
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/store/modules/auth'
import { getAnalyticsOverview } from '@/api/analytics'
import { getMyClasses } from '@/api/auth'

const authStore = useAuthStore()
const isTeacher = computed(() => ['admin', 'teacher'].includes(authStore.role))

// 班级相关状态
const myClasses = ref([])
const selectedClassId = ref(null)

// 加载班级列表
const loadMyClasses = async () => {
  if (!isTeacher.value) return
  try {
    const res = await getMyClasses()
    if (res.code === 200) {
      myClasses.value = res.data || []
      // 默认选中第一个班级（可选）
      // if (myClasses.value.length > 0) selectedClassId.value = myClasses.value[0].id
    }
  } catch (e) { /* 静默 */ }
}

// 修改 fetchOverview，传入 class_id
const fetchOverview = async () => {
  loading.value = true
  try {
    const params = { period: period.value }
    if (selectedClassId.value) {
      params.class_id = selectedClassId.value
    }
    const res = await getAnalyticsOverview(params)
    if (res.code === 200) {
      overviewData.value = res.data
    }
  } catch (error) {
    console.error('获取数据概览失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadMyClasses()
  fetchOverview()
})

watch(selectedClassId, () => fetchOverview())
```

- [ ] **Step 3: 调整标题和描述文案**

将页面标题从 `"📊 数据分析中心"` 改为根据角色动态显示：

```html
<h2>{{ isTeacher ? '📊 我的班级数据分析' : '📊 数据分析中心' }}</h2>
```

优秀学员排行的表头也相应调整：

```html
<span>🏆 {{ isTeacher ? '班级学员排行' : '优秀学员排行' }}</span>
```

---

### Task 6: 前端 - PracticeStatistics.vue 改造

**Files:**
- Modify: `admin-panel/src/views/analytics/PracticeStatistics.vue`

- [ ] **Step 1: 添加与 Overview 相同的班级选择器模式**

在 header-actions 区域添加 el-select，逻辑同 Task 5。

- [ ] **Step 2: fetchStatistics 传入 class_id**

```javascript
const fetchStatistics = async () => {
  loading.value = true
  try {
    const params = { period: period.value }
    if (scoreLevelFilter.value) params.score_level = scoreLevelFilter.value
    if (selectedClassId.value) params.class_id = selectedClassId.value
    
    const res = await getPracticeStatistics(params)
    ...
  }
}
```

- [ ] **Step 3: 标题调整**

```html
<h2>{{ isTeacher ? '✏️ 我的班级练习成绩' : '✏️ 练习成绩统计分析' }}</h2>
```

排行榜标题：

```html
<span>🏆 {{ isTeacher ? '班级练习排行榜' : '练习排行榜' }} TOP20</span>
```

---

### Task 7: 前端 - LearningProgress.vue 改造

**Files:**
- Modify: `admin-panel/src/views/analytics/LearningProgress.vue`

> **注意**: 此页面对教师的语义变化最大。当前是"个人学习时间线"，教师场景应变为"班级学习活跃度"。

- [ ] **Step 1: 添加班级选择器** (同 Task 5 模式)

- [ ] **Step 2: 调整页面标题和描述**

```html
<h2>{{ isTeacher ? '📚 我班学习情况' : '📚 学习进度分析' }}</h2>
```

- [ ] **Step 3: 调整指标卡片含义标签**

当 `isTeacher` 为 true 时，指标含义从"我读了多少"变为"班级共学习了多少":

| 指标 | 学生含义 | 教师含义 |
|------|---------|---------|
| 总阅读时长 | 个人累计 | 班级学生累计总和 |
| 完成数量 | 个人完成 | 班级完成人数 |
| 日均学习 | 个人日均 | 班级人均日均 |

```html
<div style="font-size: 13px; color: #909399;">
  {{ isTeacher ? '班级总阅读时长' : '总阅读时长' }}
</div>
```

- [ ] **Step 4: fetchProgress 传入 class_id**

```javascript
const params = { period: period.value }
if (categoryFilter.value) params.category = categoryFilter.value
if (selectedClassId.value) params.class_id = selectedClassId.value
```

---

### Task 8: 可选增强 - 空状态提示

**Files:**
- Modify: 以上3个 Vue 文件

- [ ] **Step 1: 当教师没有管理任何学生时，显示友好提示**

在3个页面的 template 中添加空状态判断：

```html
<el-empty 
  v-if="isTeacher && myClasses.length === 0 && !loading"
  description="您暂未管理任何班级和学生"
  :image-size="120"
>
  <el-button type="primary">联系管理员分配班级</el-button>
</el-empty>

<el-row :gutter="20" v-loading="loading" v-else>
  <!-- 原有内容 -->
</el-row>
```

---

## 执行顺序建议

```
Task 1 (后端基础) → Task 2 (后端API改造) → Task 3 (新接口) 
    → Task 4 (前端API) → Task 5+6+7 (前端页面，可并行) → Task 8 (增强)
```

## 验证清单

| # | 验证项 | 方法 |
|---|--------|------|
| 1 | 管理员登录 → 数据不变 | 全量数据显示正常 |
| 2 | 教师登录 → 仅本班数据 | 数据量为该教师学生子集 |
| 3 | 教师切换班级 → 数据联动 | 选择不同班级数据正确切换 |
| 4 | 教师无学生 → 空状态 | 显示友好提示 |
| 5 | 学生登录 → 个人数据不受影响 | 学生仍只看自己数据 |
| 6 | 排行榜 → 仅本班学生 | 不出现其他班级学生 |

## 可能的后续扩展 (不在本次范围内)

- [ ] 教师班级管理页面（分配/移除学生）
- [ ] 班级维度对比报表（多班级横向对比）
- [ ] 家长视角的数据查看（如需要）
- [ ] 数据导出时带上班级筛选条件
