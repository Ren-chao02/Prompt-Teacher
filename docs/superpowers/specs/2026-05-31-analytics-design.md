# Phase 5: 数据分析与可视化系统 - 设计文档

**日期:** 2026-05-31  
**状态:** 已批准 ✅  
**版本:** v1.0  

---

## 1. 项目概述

### 1.1 目标
构建统一的数据分析中心，为管理员、教师、学生三个角色提供学习进度追踪和练习成绩分析能力，通过ECharts可视化图表直观展示数据洞察。

### 1.2 核心价值
- **数据驱动决策** - 基于真实数据优化教学内容和策略
- **个性化学习路径** - 帮助学生了解自身薄弱环节
- **教学效果评估** - 让教师掌握班级整体学习状况
- **平台运营监控** - 助力管理者了解平台健康度

### 1.3 范围界定
**包含：**
- ✅ 学习进度分析（时间线、完成率、热门内容）
- ✅ 练习成绩统计（趋势、分布、对比、薄弱点）
- ✅ 多角色权限控制
- ✅ 数据导出功能

**不包含（后续Phase）：**
- ❌ 用户活跃度深度分析（可扩展）
- ❌ 内容热度与推荐算法（Phase 6+）
- ❌ 实时数据推送（WebSocket，Phase 7+）

---

## 2. 架构设计

### 2.1 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| **前端框架** | Vue 3 (Composition API) | ^3.3 |
| **UI组件库** | Element Plus | ^2.4 |
| **图表库** | ECharts 5 | ^5.4 |
| **状态管理** | Pinia | ^2.1 |
| **后端框架** | Django REST Framework | ^3.14 |
| **数据库** | SQLite (开发) / PostgreSQL (生产) | - |
| **缓存** | Redis (可选) | ^7.0 |

### 2.2 目录结构

```
analytics/                              # Django App
├── __init__.py
├── apps.py                             # App配置
├── models.py                           # 预留统计模型（可选）
├── admin.py                            # Django Admin
├── api/
│   ├── __init__.py
│   ├── urls.py                         # API路由配置
│   ├── views.py                        # 统计视图集
│   └── serializers.py                  # 响应序列化器
├── services/
│   ├── __init__.py
│   ├── base_analytics.py               # 基础分析服务类
│   ├── learning_analytics.py           # 学习进度分析
│   └── practice_analytics.py           # 练习成绩分析
└── tests.py                            # 单元测试

admin-panel/src/
├── api/
│   └── analytics.js                    # API请求封装
├── views/analytics/
│   ├── index.vue                       # 数据概览页
│   ├── learning/
│   │   └── progress.vue                # 学习进度详情
│   └── practice/
│       └── statistics.vue              # 练习成绩统计
└── components/charts/
    ├── BaseChart.vue                   # ECharts基础封装
    ├── LineChart.vue                   # 折线图
    ├── BarChart.vue                    # 柱状图
    ├── PieChart.vue                    # 饼图/环形图
    └── RadarChart.vue                  # 雷达图
```

---

## 3. 数据模型设计

### 3.1 策略选择：实时聚合 + 缓存

**决策理由：**
- 初期数据量小 (< 10万记录)，实时查询性能足够
- 避免维护预计算表的复杂度
- 通过Redis缓存 (TTL=5分钟) 平衡性能和实时性

**未来扩展点：**
- 当单表 > 50万记录时，引入定时任务预计算
- 使用Materialized View或独立统计表

### 3.2 缓存键设计

```python
CACHE_KEYS = {
    'overview': 'analytics:overview:{role}:{period}',
    'learning_progress': 'analytics:learning:{user_id}:{period}',
    'practice_stats': 'analytics:practice:{user_id}:{scenario_id}:{period}'
}

CACHE_TTL = 300  # 5分钟
```

---

## 4. API接口设计

### 4.1 概览接口

**端点:** `GET /api/v1/analytics/overview/`

**查询参数:**
```typescript
interface OverviewParams {
  period?: '7d' | '30d' | '90d'  // 时间范围，默认30d
}
```

**响应结构:**
```typescript
interface OverviewResponse {
  code: number
  message: string
  data: {
    learning: {
      total_materials: number        // 总内容数
      today_new: number              // 今日新增
      completion_rate: number        // 整体完成率 (%)
      avg_read_time: number          // 平均阅读时长(分钟)
      daily_trend: Array<{           // 每日趋势
        date: string
        count: number
        read_time: number
      }>
    }
    practice: {
      total_records: number          // 总练习次数
      avg_score: number              // 平均分
      pass_rate: number              // 通过率 (%)
      daily_trend: Array<{           // 每日趋势
        date: string
        count: number
        avg_score: number
      }>
    }
    users: {
      active_today: number           // 今日活跃用户
      new_this_week: number          // 本周新增
      retention_rate: number         // 留存率 (%)
    }
    top_content: Array<{             // 热门内容 Top10
      id: number
      title: string
      category: string
      views: number
      completions: number
    }>
    top_users?: Array<{              // 优秀学员 (admin/teacher)
      id: number
      username: string
      role: string
      total_practices: number
      avg_score: number
    }>
  }
}
```

**权限逻辑:**
```python
def get_overview_statistics(self, request):
    user = request.user
    
    if user.role == 'student':
        # 学生只看个人数据
        data = self._get_student_overview(user)
    elif user.role == 'teacher':
        # 教师看所教班级数据
        data = self._get_teacher_overview(user)
    else:
        # 管理员看全平台数据
        data = self._get_admin_overview()
    
    return Response(data)
```

---

### 4.2 学习进度接口

**端点:** `GET /api/v1/analytics/learning/progress/`

**查询参数:**
```typescript
interface LearningProgressParams {
  user_id?: number                   // 用户ID (可选,不传则看全局)
  period?: '7d' | '30d' | '90d'     // 时间范围
  category?: string                  // 内容分类筛选
}
```

**响应结构:**
```typescript
interface LearningProgressResponse {
  code: number
  message: string
  data: {
    timeline: {                      // 学习时间线
      dates: string[]
      read_minutes: number[]
      completed_count: number[]
    }
    completion: {                    // 完成情况
      by_category: Record<string, {
        total: number
        completed: number
        rate: number                 // 完成率(%)
      }>
      overall_rate: number
    }
    popular_content: Array<{         // 热门内容
      id: number
      title: string
      views: number
      completions: number
      avg_read_time: number
    }>
    reading_habits: {                // 学习习惯
      peak_hours: number[]           // 高峰时段 [9, 14, 20]
      avg_session_duration: number   // 平均单次时长(分钟)
      preferred_categories: string[] // 偏好分类
      active_days_per_week: number   // 每周活跃天数
    }
  }
}
```

**核心聚合SQL示例:**
```python
from django.db.models import Count, Avg, Sum
from learning.models import LearningMaterial, ReadLog

def get_timeline_stats(user_id, period):
    """
    查询近N天每日学习时长和完成数
    """
    since = timezone.now() - timedelta(days=int(period[:-1]))
    
    timeline = (
        ReadLog.objects
        .filter(user_id=user_id, created_at__gte=since)
        .dates('created_at', 'day')
        .annotate(
            read_minutes=Sum('duration_seconds') / 60,
            completed_count=Count('id', filter=Q(status='completed'))
        )
        .order_by('created_at')
        .values_list('created_at', 'read_minutes', 'completed_count')
    )
    
    return {
        'dates': [str(t[0]) for t in timeline],
        'read_minutes': [t[1] or 0 for t in timeline],
        'completed_count': [t[2] or 0 for t in timeline]
    }
```

---

### 4.3 练习统计接口

**端点:** `GET /api/v1/analytics/practice/statistics/`

**查询参数:**
```typescript
interface PracticeStatisticsParams {
  user_id?: number                   // 用户ID (可选)
  scenario_id?: number               // 场景ID (可选)
  topic_id?: number                  // 主题ID (可选)
  score_level?: string               // 等级筛选 excellent/good/average/fail
  period?: '7d' | '30d' | '90d'
}
```

**响应结构:**
```typescript
interface PracticeStatisticsResponse {
  code: number
  message: string
  data: {
    score_trend: {                   // 成绩趋势
      dates: string[]
      scores: number[]
      avg_score: number
      trend: 'up' | 'down' | 'stable'
    }
    distribution: {                  // 分数分布
      'excellent (90-100)': number
      'good (80-89)': number
      'average (70-79)': number
      'below_average (60-69)': number
      'fail (0-59)': number
      statistics: {
        mean: number
        median: number
        std_dev: number
      }
    }
    scenario_comparison: Array<{     // 场景表现对比
      scenario_id: number
      scenario_title: string
      icon: string
      difficulty: string
      avg_score: number
      practice_count: number
      best_score: number
      improvement_rate: string       // "+15%" / "-5%"
    }>
    weak_points: Array<{             // 薄弱点识别
      topic_id: number
      topic_title: string
      error_rate: number             // 错误率(%)
      total_attempts: number
      suggestion: string             // 改进建议
    }>
    ranking?: Array<{                // 排行榜 (需权限)
      rank: number
      user_id: number
      username: string
      avatar: string | null
      total_practices: number
      avg_score: number
      best_score: number
    }>
  }
}
```

**高级聚合示例:**
```python
import numpy as np
from django.db.models import Count, Avg, StdDev

def get_score_distribution(user_id):
    """
    计算分数分布 + 统计指标
    """
    scores = list(
        PracticeRecord.objects
        .filter(user_id=user_id)
        .values_list('overall_score', flat=True)
    )
    
    if not scores:
        return empty_distribution()
    
    # 分数段划分
    bins = [(90, 100), (80, 89), (70, 79), (60, 59), (0, 59)]
    distribution = {}
    for low, high in bins:
        key = f"{'excellent' if low >= 90 else 'good' if low >= 80 else 'average' if low >= 70 else 'below_average' if low >= 60 else 'fail'} ({low}-{high})"
        distribution[key] = len([s for s in scores if low <= s <= high])
    
    # 统计指标
    scores_array = np.array(scores)
    distribution['statistics'] = {
        'mean': round(float(np.mean(scores_array)), 1),
        'median': round(float(np.median(scores_array)), 1),
        'std_dev': round(float(np.std(scores_array)), 1)
    }
    
    return distribution
```

---

## 5. 前端页面设计

### 5.1 页面路由配置

```javascript
// router/index.js 新增
{
  path: '/admin/analytics',
  component: AdminLayout,
  meta: { requiresAuth: true, icon: 'DataAnalysis', title: '数据分析' },
  children: [
    {
      path: '',
      name: 'AnalyticsOverview',
      component: () => import('@/views/analytics/index.vue'),
      meta: { title: '数据概览', roles: ['admin', 'teacher', 'student'] }
    },
    {
      path: 'learning/progress',
      name: 'LearningProgress',
      component: () => import('@/views/analytics/learning/progress.vue'),
      meta: { title: '学习进度', roles: ['admin', 'teacher', 'student'] }
    },
    {
      path: 'practice/statistics',
      name: 'PracticeStatistics',
      component: () => import('@/views/analytics/practice/statistics.vue'),
      meta: { title: '练习统计', roles: ['admin', 'teacher', 'student'] }
    }
  ]
}
```

### 5.2 全局概览页布局

```
┌─────────────────────────────────────────────────────────────┐
│ 📊 数据分析中心                        [📅 近30天 ▼] [🔄]  │
├──────┬──────┬──────┬────────────────────────────────────────┤
│ 📖   │ 🎯   │ 👥   │                                        │
│ 学习  │ 练习  │ 用户  │     📈 平台活跃度趋势 (7天)            │
│      │      │      │     [折线图 AreaChart]                   │
│ 150  │ 1200 │ 45   │                                        │
│ +5   │ 82.5 │ +12  │                                        │
│ 68%  │ 75%  │ 85%  │                                        │
├──────┴──────┴──────┴────────────────────────────────────────┤
│ 🔥 热门内容 Top 10              │ 🏆 学员练习排行榜            │
│ [横向柱状图 BarChart]           │ [表格 Table + 徽章 Tag]      │
└─────────────────────────────────────────────────────────────┘
```

**关键组件:**
```vue
<template>
  <div class="analytics-overview">
    <!-- 页头 -->
    <div class="page-header">
      <h2>📊 数据分析中心</h2>
      <el-date-picker v-model="period" type="daterange" />
      <el-button @click="refreshData">刷新</el-button>
    </div>

    <!-- 核心指标卡片 -->
    <el-row :gutter="16" class="stats-cards">
      <el-col :span="6" v-for="card in statCards" :key="card.title">
        <StatCard :data="card" />
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="16">
      <el-col :span="24">
        <LineChart :option="trendOption" title="活跃度趋势" />
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="12">
        <BarChart :option="popularContentOption" title="热门内容" />
      </el-col>
      <el-col :span="12">
        <RankingTable :data="topUsers" title="优秀学员" />
      </el-col>
    </el-row>
  </div>
</template>
```

### 5.3 学习进度页图表配置

**时间线面积图:**
```javascript
const timelineOption = {
  title: { text: '近30天学习时长趋势', left: 'center' },
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: ['05-01', '05-02', ..., '05-30'],
    axisLabel: { rotate: 45 }
  },
  yAxis: [
    { type: 'value', name: '分钟', position: 'left' },
    { type: 'value', name: '完成数', position: 'right' }
  ],
  series: [
    {
      name: '学习时长',
      type: 'line',
      areaStyle: { opacity: 0.3 },
      data: [25, 30, 0, 45, ...],
      smooth: true
    },
    {
      name: '完成数',
      type: 'bar',
      yAxisIndex: 1,
      data: [2, 1, 0, 3, ...]
    }
  ]
}
```

**完成率环形图:**
```javascript
const completionOption = {
  title: { text: '内容完成率', left: 'center' },
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { orient: 'vertical', left: 'left' },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    avoidLabelOverlap: false,
    label: { show: false, position: 'center' },
    emphasis: {
      label: { show: true, fontSize: 18, fontWeight: 'bold' }
    },
    data: [
      { value: 1048, name: '已完成', itemStyle: { color: '#67C23A' } },
      { value: 735, name: '进行中', itemStyle: { color: '#E6A23C' } },
      { value: 580, name: '未开始', itemStyle: { color: '#909399' } }
    ]
  }]
}
```

### 5.4 练习统计页图表配置

**成绩趋势折线图:**
```javascript
const scoreTrendOption = {
  title: { text: '近期成绩变化', left: 'center' },
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: dates },
  yAxis: { type: 'value', min: 0, max: 100, name: '分数' },
  markLine: {
    data: [{ type: 'average', name: '平均分' }]
  },
  series: [{
    type: 'line',
    data: scores,
    markPoint: {
      data: [
        { type: 'max', name: '最高分' },
        { type: 'min', name: '最低分' }
      ]
    },
    smooth: true,
    lineStyle: { width: 3 },
    areaStyle: { opacity: 0.1 }
  }]
}
```

**分数分布直方图:**
```javascript
const distributionOption = {
  title: { text: '成绩分布', left: 'center' },
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: Object.keys(distribution) },
  yAxis: { type: 'value', name: '人数' },
  series: [{
    type: 'bar',
    data: Object.values(distribution),
    itemStyle: {
      color: (params) => {
        const colors = ['#F56C6C', '#E6A23C', '#409EFF', '#67C23A', '#67C23A']
        return colors[params.dataIndex]
      }
    },
    label: { show: true, position: 'top' }
  }]
}
```

**场景对比雷达图:**
```javascript
const radarOption = {
  title: { text: '各场景能力雷达图', left: 'center' },
  legend: { data: ['你的表现', '平均水平'] },
  radar: {
    indicator: [
      { name: '准确性', max: 100 },
      { name: '速度', max: 100 },
      { name: '稳定性', max: 100 },
      { name: '难度适应', max: 100 },
      { name: '创新性', max: 100 }
    ]
  },
  series: [{
    type: 'radar',
    data: [
      { value: [88, 75, 92, 80, 85], name: '你的表现' },
      { value: [78, 72, 80, 75, 70], name: '平均水平' }
    ]
  }]
}
```

---

## 6. 权限与安全设计

### 6.1 角色数据隔离矩阵

| 数据维度 | 管理员 | 教师 | 学生 |
|---------|--------|------|------|
| **全局统计** | ✅ 全平台 | ❌ 无权访问 | ❌ 无权访问 |
| **班级数据** | ✅ 所有班级 | ✅ 所教班级 | ❌ 无权访问 |
| **个人数据** | ✅ 可查看任意用户 | ✅ 可查看学生 | ✅ 仅自己 |
| **导出功能** | ✅ 全量导出 | ✅ 班级导出 | ✅ 个人导出 |

### 6.2 权限实现代码

```python
# analytics/api/views.py
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdminUser, IsTeacherUser

class AnalyticsPermission(IsAuthenticated):
    """
    自定义权限类 - 基于角色控制数据可见范围
    """
    def has_permission(self, request, view):
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return True

class AnalyticsBaseViewSet(viewsets.GenericViewSet):
    permission_classes = [AnalyticsPermission]
    
    def get_queryset_based_on_role(self):
        """根据角色返回不同的数据集"""
        user = self.request.user
        
        if user.role == 'student':
            return self.queryset.filter(user=user)
        elif user.role == 'teacher':
            # TODO: 获取教师管理的班级/学生列表
            student_ids = self._get_teacher_students(user)
            return self.queryset.filter(user_id__in=student_ids)
        else:
            return self.queryset  # admin看到所有
```

---

## 7. 性能优化策略

### 7.1 缓存层

```python
# services/base_analytics.py
from django.core.cache import cache
from functools import wraps

def cache_analytics_result(timeout=300):
    """
    缓存装饰器 - 自动缓存分析结果
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{hash(frozenset(kwargs.items()))}"
            
            # 尝试从缓存获取
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # 执行查询
            result = func(*args, **kwargs)
            
            # 写入缓存
            cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator

class BaseAnalyticsService:
    @cache_analytics_result(timeout=300)  # 5分钟缓存
    def get_statistics(self, **kwargs):
        pass
```

### 7.2 数据库优化

**索引建议:**
```python
# learning/models.py - ReadLog模型添加索引
class ReadLog(models.Model):
    user = models.ForeignKey(...)
    material = models.ForeignKey(...)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),  # 用户时间线查询
            models.Index(fields=['material', '-created_at']),  # 内容热度查询
            models.Index(fields=['user', 'material']),  # 去重查询
        ]

# practice/models.py - PracticeRecord模型索引
class PracticeRecord(models.Model):
    user = models.ForeignKey(...)
    scenario = models.ForeignKey(...)
    overall_score = models.IntegerField(...)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['scenario', '-created_at']),
            models.Index(fields=['-overall_score']),  # 排行榜查询
        ]
```

### 7.3 分页与懒加载

```javascript
// 大数据量时使用虚拟滚动或分页加载
const handleScroll = debounce(() => {
  if (nearBottom.value && !loading.value) {
    loadMoreData()  # 加载下一页
  }
}, 200)
```

---

## 8. 导出功能

### 8.1 Excel导出

**后端实现:**
```python
import pandas as pd
from django.http import HttpResponse

@action(detail=False, methods=['post'])
def export_excel(self, request):
    format_type = request.data.get('format', 'excel')
    data = self.get_statistics(request)
    
    df = pd.DataFrame(data['details'])
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="analytics_{timezone.now().date()}.xlsx"'
    
    df.to_excel(response, index=False, engine='openpyxl')
    return response
```

### 8.2 PDF报告 (可选)

使用 `reportlab` 或 `weasyprint` 生成带图表的PDF报告。

---

## 9. 测试策略

### 9.1 单元测试

```python
# analytics/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from analytics.services import LearningAnalyticsService

class AnalyticsServiceTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            role='student'
        )
    
    def test_get_empty_progress(self):
        """无数据时的空结果"""
        result = LearningAnalyticsService.get_progress_stats(
            user_id=self.user.id
        )
        self.assertEqual(result['timeline']['dates'], [])
        self.assertEqual(result['completion']['overall_rate'], 0)
    
    def test_cache_mechanism(self):
        """验证缓存生效"""
        # 第一次调用 - 应该执行查询
        result1 = LearningAnalyticsService.get_progress_stats(
            user_id=self.user.id
        )
        
        # 第二次调用 - 应该从缓存返回
        result2 = LearningAnalyticsService.get_progress_stats(
            user_id=self.user.id
        )
        
        self.assertEqual(result1, result2)
```

### 9.2 集成测试

```python
class AnalyticsAPITest(APITestCase):
    def setUp(self):
        self.admin = create_user(role='admin')
        self.client.force_authenticate(user=self.admin)
    
    def test_overview_endpoint(self):
        """测试概览接口返回正确结构"""
        response = self.client.get('/api/v1/analytics/overview/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('learning', response.data['data'])
        self.assertIn('practice', response.data['data'])
        self.assertIn('users', response.data['data'])
    
    def test_student_cannot_see_global_data(self):
        """学生无法访问全局统计数据"""
        student = create_user(role='student')
        self.client.force_authenticate(user=student)
        
        response = self.client.get('/api/v1/analytics/overview/')
        
        # 学生应该只看到个人数据
        self.assertNotIn('top_users', response.data['data'])
```

---

## 10. 实施计划

### Phase 5.1: 基础框架搭建 (预计2天)

**任务清单:**
- [ ] 创建 `analytics` Django App并注册
- [ ] 设计基础服务类 `BaseAnalyticsService`
- [ ] 实现概览API骨架 `/api/v1/analytics/overview/`
- [ ] 创建前端路由和页面目录结构
- [ ] 安装并封装 ECharts 基础组件 `BaseChart.vue`
- [ ] 实现4种图表组件 (Line/Bar/Pie/Radar)

**验收标准:**
- ✅ Django App注册成功，可访问 `/api/v1/analytics/`
- ✅ 前端路由 `/admin/analytics` 可正常跳转
- ✅ ECharts渲染空白图表无报错

---

### Phase 5.2: 学习进度模块 (预计3天)

**任务清单:**
- [ ] 实现 `LearningAnalyticsService` 服务类
- [ ] 开发学习时间线聚合查询 (按日/周/月)
- [ ] 开发内容完成率计算逻辑
- [ ] 开发热门内容排行算法
- [ ] 实现学习习惯分析 (高峰时段等)
- [ ] 前端页面: 时间线面积图
- [ ] 前端页面: 完成率环形图
- [ ] 前端页面: 热门内容柱状图
- [ ] 添加时间范围筛选器
- [ ] 实现缓存机制

**验收标准:**
- ✅ API返回正确的学习进度数据
- ✅ 图表展示流畅，支持交互 (tooltip/legend/缩放)
- ✅ 切换时间范围后数据更新正确
- ✅ 缓存命中时响应时间 < 100ms

---

### Phase 5.3: 练习统计模块 (预计3天)

**任务清单:**
- [ ] 实现 `PracticeAnalyticsService` 服务类
- [ ] 开发成绩趋势聚合 (含移动平均)
- [ ] 开发分数分布统计 (直方图)
- [ ] 开发场景对比分析 (多维度)
- [ ] 实现薄弱知识点识别算法
- [ ] 实现排行榜逻辑 (权限控制)
- [ ] 前端页面: 成绩趋势折线图 (含标记点)
- [ ] 前端页面: 分布直方图 (颜色编码)
- [ ] 前端页面: 场景雷达图
- [ ] 前端页面: 薄弱点词云/树图

**验收标准:**
- ✅ 统计指标准确 (均值/中位数/标准差)
- ✅ 雷达图能清晰展示能力维度差异
- ✅ 薄弱点建议合理且可操作
- ✅ 排行榜仅对有权限用户显示

---

### Phase 5.4: 权限优化与完善 (预计2天)

**任务清单:**
- [ ] 实现多角色数据过滤中间件
- [ ] 完善 Admin/Teacher/Student 三套数据视图
- [ ] 添加数据导出功能 (Excel格式)
- [ ] 性能优化: 添加数据库索引
- [ ] 性能优化: Redis缓存集成 (可选)
- [ ] 错误处理: 边界情况覆盖 (空数据/超时/权限不足)
- [ ] UI优化: 加载状态/空状态/错误提示
- [ ] 编写单元测试 (覆盖率 > 80%)
- [ ] 编写集成测试 (核心流程)
- [ ] 文档更新: API文档 + 使用指南

**验收标准:**
- ✅ 三个角色看到的差异化数据正确
- ✅ 导出的Excel数据完整且格式美观
- ✅ API平均响应时间 < 500ms (P95)
- ✅ 测试全部通过，无回归Bug

---

## 11. 风险与应对

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|----------|
| **性能瓶颈** | 大数据量查询慢 | 中 | 引入缓存 + 异步预计算 |
| **ECharts内存泄漏** | 页面卡顿 | 低 | 组件销毁时dispose实例 |
| **权限漏洞** | 数据泄露 | 低 | 严格的权限测试 + 代码审查 |
| **图表兼容性** | 移动端显示异常 | 中 | 响应式设计 + 降级方案 |
| **需求变更** | 返工成本高 | 中 | 模块化设计 + 配置化 |

---

## 12. 未来扩展路线图

### Phase 5.x (可选增强)
- [ ] **实时仪表盘** - WebSocket推送实时数据
- [ ] **智能预警** - 成绩异常下降自动通知
- [ ] **对比分析** - 不同时间段/群体的对比
- [ ] **自定义报表** - 用户自选指标组合

### Phase 6+: 与其他模块整合
- [ ] **推荐系统集成** - 基于薄弱点推荐学习内容
- [ ] **成就系统** - 解锁徽章/证书
- [ ] **AI辅助分析** - LLM生成个性化学习建议

---

## 13. 总结

本设计文档定义了 **Prompt Teacher 平台数据分析与可视化系统** 的完整技术方案，涵盖：

✅ **三大核心模块** (概览/学习/练习)  
✅ **多角色权限体系** (Admin/Teacher/Student)  
✅ **详细API接口规范** (12+个端点)  
✅ **丰富图表类型** (折线/柱状/饼图/雷达)  
✅ **性能保障机制** (缓存/索引/分页)  
✅ **完整测试策略** (单元/集成/E2E)  
✅ **渐进式实施计划** (4阶段，共10天)  

**预期成果：**
- 为平台运营提供数据支撑
- 提升教师教学效果评估能力
- 帮助学生了解自身学习状况
- 打造专业级的数据分析体验

---

**文档版本历史:**
- v1.0 (2026-05-31): 初始设计，已获批准 ✅

**下一步:** 开始实施 Phase 5.1 - 基础框架搭建
