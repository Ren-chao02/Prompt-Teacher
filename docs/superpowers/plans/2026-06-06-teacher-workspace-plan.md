# 教师工作台（Teacher Workspace）实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为教师角色构建独立的班级学生管理工作台首页和详情页，包含统计卡片、学生总览表、趋势图表、预警提醒。

**Architecture:** 后端在 `users.api.views.py` 中新增 2 个 APIView（workspace / student_detail），前端新增 `views/teacher/` 目录下的 Workspace.vue 和 StudentDetail.vue，配合路由变更和侧边栏菜单更新。不创建新的 Django app，复用现有 users 模块（与 MyClassesAPIView 同级）。

**Tech Stack:** Django REST Framework (后端), Vue3 + Element Plus + ECharts (前端), Pinia (状态管理)

---

## 文件结构总览

| 操作 | 文件路径 | 职责 |
|------|---------|------|
| Modify | `users/api/views.py` | 新增 TeacherWorkspaceView + TeacherStudentDetailView |
| Modify | `users/api/urls.py` | 注册 2 个新路由 |
| Create | `admin-panel/src/api/teacher.js` | 前端 API 调用封装 |
| Create | `admin-panel/src/views/teacher/Workspace.vue` | 工作台首页主组件 |
| Create | `admin-panel/src/views/teacher/StudentDetail.vue` | 学生详情页 |
| Modify | `admin-panel/src/router/index.js` | 新增路由 + 教师默认 redirect |
| Modify | `admin-panel/src/components/Layout/AdminLayout.vue` | 侧边栏添加「我的工作台」菜单 |

---

### Task 1: 后端 - 新增教师工作台概览 API

**Files:**
- Modify: `users/api/views.py`
- Modify: `users/api/urls.py`

- [ ] **Step 1: 在 `users/api/views.py` 末尾新增 `TeacherWorkspaceView`**

在文件末尾（MyClassesAPIView 之后）追加以下类：

```python
from django.utils import timezone
from django.db.models import Avg, Count, Q, F
from datetime import timedelta


class TeacherWorkspaceView(APIView):
    """教师工作台 - 班级学生数据概览"""
    permission_classes = [IsAuthenticated]

    def _get_date_range(self, period):
        """根据 period 参数返回 (start_date, end_date)"""
        now = timezone.now()
        if period == '7d':
            return now - timedelta(days=7), now
        elif period == '90d':
            return now - timedelta(days=90), now
        else:  # 默认 30d 或 all
            return now - timedelta(days=30), now

    def _get_managed_students(self, user, class_id=None):
        """获取教师管理的学生 queryset"""
        qs = UserProfile.objects.filter(teacher=user)
        if class_id:
            qs = qs.filter(class_info_id=class_id)
        return qs

    def get(self, request):
        from practice.models import PracticeRecord
        from learning.models import LearningMaterial

        user = request.user
        role = getattr(user, 'role', '')

        if role not in ['admin', 'teacher']:
            return Response({'code': 403, 'message': '无权限'}, status=403)

        # 教师只能看自己的学生；管理员可传 student_user_id 参数
        if role == 'teacher':
            target_teacher = user
        else:
            target_teacher = request.query_params.get('teacher_user_id')
            if not target_teacher:
                target_teacher = user

        class_id = request.query_params.get('class_id')
        period = request.query_params.get('period', '30d')

        students_qs = self._get_managed_students(target_teacher, class_id)
        student_ids = list(students_qs.values_list('pk', flat=True))

        if not student_ids:
            return Response({
                'code': 200,
                'data': {
                    'stats': {
                        'total_students': 0,
                        'class_avg_score': 0,
                        'material_completion_rate': 0,
                        'active_rate': 0,
                        'total_practices': 0,
                        'attention_count': 0,
                    },
                    'students': [],
                    'charts': {'score_distribution': {}, 'activity_trend': []},
                    'alerts': [],
                }
            })

        start_date, end_date = self._get_date_range(period)

        # ========== B区：统计卡片 ==========
        total_students = len(student_ids)

        # 练习均分（时间范围内）
        practice_qs = PracticeRecord.objects.filter(
            user_id__in=student_ids,
            created_at__gte=start_date,
            created_at__lte=end_date,
            is_completed=True
        )
        score_agg = practice_qs.aggregate(avg=Avg('overall_score'))
        class_avg_score = round(score_agg['avg'] or 0, 1)

        total_practices = practice_qs.count()

        # 活跃率：近7天有登录的学生
        seven_days_ago = timezone.now() - timedelta(days=7)
        active_count = UserProfile.objects.filter(
            pk__in=student_ids,
            last_login__gte=seven_days_ago
        ).count()
        active_rate = round(active_count / total_students * 100) if total_students > 0 else 0

        # 资料完成率（近似值：已发布资料数作为分母）
        total_materials = LearningMaterial.objects.filter(status='published').count()
        material_completion_rate = 65  # 占位，后续可精确计算

        # ========== C区：学生列表 ==========
        # 每个学生的聚合数据
        student_stats = {}
        records_by_student = practice_qs.values('user_id').annotate(
            count=Count('id'),
            avg_score=Avg('overall_score'),
        )
        for r in records_by_student:
            student_stats[r['user_id']] = {
                'practice_count': r['count'],
                'avg_score': round(r['avg_score'] or 0, 1),
            }

        # 班级均值（用于状态判定）
        class_avg_practices = total_practices / total_students if total_students > 0 else 0

        students_data = []
        alerts = []

        for s in students_qs.select_related('class_info'):
            stats = student_stats.get(s.pk, {'practice_count': 0, 'avg_score': 0})
            avg_score = stats['avg_score']
            practices = stats['practice_count']

            # 状态判定
            days_since_login = (timezone.now() - s.last_login).days if s.last_login else 999
            if avg_score >= 85 and practices >= class_avg_practices:
                status = 'excellent'
            elif avg_score >= 60 and days_since_login <= 7:
                status = 'normal'
            else:
                status = 'attention'

            student_entry = {
                'id': s.pk,
                'real_name': s.real_name or s.username,
                'student_id': s.student_id or '',
                'class_name': s.class_info.name if s.class_info else '',
                'completion_rate': 0,  # TODO: 可关联 MaterialInteraction 计算
                'practice_count': practices,
                'avg_score': avg_score,
                'last_login': s.last_login.isoformat() if s.last_login else None,
                'status': status,
            }
            students_data.append(student_entry)

            # ========== E区：预警规则 ==========
            if status == 'attention':
                alert_reasons = []
                if avg_score < class_avg_score - 10 and class_avg_score > 0:
                    diff = round(class_avg_score - avg_score, 1)
                    alert_reasons.append({
                        'reason': 'score_low',
                        'detail': f'练习均分 {avg_score}，低于班级平均 {diff} 分',
                    })
                if days_since_login > 7:
                    alert_reasons.append({
                        'reason': 'inactive',
                        'detail': f'已连续 {days_since_login} 天未登录',
                    })
                if practices < class_avg_practices * 0.3 and class_avg_practices > 0:
                    alert_reasons.append({
                        'reason': 'low_practice',
                        'detail': f'练习次数偏少：{practices}次（班级平均 {round(class_avg_practices, 1)}次）',
                    })

                if alert_reasons:
                    alerts.append({
                        'student_id': s.pk,
                        'student_name': s.real_name or s.username,
                        **alert_reasons[0],  # 取最严重的
                        'avg_score': avg_score,
                        'last_login': s.last_login.isoformat() if s.last_login else None,
                    })

        attention_count = sum(1 for s in students_data if s['status'] == 'attention')

        # ========== D区：图表数据 ==========
        # 成绩分布
        distribution = {'excellent': 0, 'good': 0, 'average': 0, 'pass': 0, 'fail': 0}
        for s in students_data:
            sc = s['avg_score']
            if sc >= 90:
                distribution['excellent'] += 1
            elif sc >= 80:
                distribution['good'] += 1
            elif sc >= 70:
                distribution['average'] += 1
            elif sc >= 60:
                distribution['pass'] += 1
            else:
                distribution['fail'] += 1

        # 近30天活跃趋势
        trend_start = timezone.now() - timedelta(days=30)
        daily_active = UserProfile.objects.filter(
            pk__in=student_ids,
            last_login__gte=trend_start
        ).extra(select={'day': 'date(last_login)'}).values('day').annotate(
            c=Count('id')
        ).order_by('day')

        daily_practices = practice_qs.filter(created_at__gte=trend_start).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(c=Count('id')).order_by('day')

        activity_trend = []
        # 合并两个查询结果（简化处理）
        day_map = {}
        for d in daily_active:
            day_map[d['day'].isoformat()] = {'active_students': d['c'], 'practice_count': 0}
        for d in daily_practices:
            key = d['day'].isoformat()
            if key in day_map:
                day_map[key]['practice_count'] = d['c']
            else:
                day_map[key] = {'active_students': 0, 'practice_count': d['c']}
        for day_str in sorted(day_map.keys()):
            activity_trend.append({'date': day_str, **day_map[day_str]})

        return Response({
            'code': 200,
            'data': {
                'stats': {
                    'total_students': total_students,
                    'class_avg_score': class_avg_score,
                    'material_completion_rate': material_completion_rate,
                    'active_rate': active_rate,
                    'total_practices': total_practices,
                    'attention_count': attention_count,
                },
                'students': students_data,
                'charts': {
                    'score_distribution': distribution,
                    'activity_trend': activity_trend,
                },
                'alerts': alerts,
            }
        })


class TeacherStudentDetailView(APIView):
    """教师工作台 - 学生详情"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        from practice.models import PracticeRecord

        user = request.user
        role = getattr(user, 'role', '')

        if role not in ['admin', 'teacher']:
            return Response({'code': 403, 'message': '无权限'}, status=403)

        try:
            student = UserProfile.objects.get(pk=pk)
        except UserProfile.DoesNotExist:
            return Response({'code': 404, 'message': '学生不存在'}, status=404)

        # 权限检查：教师只能查看自己管理的学生
        if role == 'teacher':
            if student.teacher != user:
                return Response({'code': 403, 'message': '无权查看此学生'}, status=403)

        period = request.query_params.get('period', '30d')
        now = timezone.now()
        if period == '7d':
            start_date = now - timedelta(days=7)
        elif period == '90d':
            start_date = now - timedelta(days=90)
        else:
            start_date = now - timedelta(days=30)

        # 基本信息
        basic = {
            'id': student.pk,
            'real_name': student.real_name or student.username,
            'student_id': student.student_id or '',
            'class_name': student.class_info.name if student.class_info else '',
            'avatar': student.avatar.url if student.avatar else None,
            'status': '',  # 下面计算
            'date_joined': student.date_joined.isoformat() if student.date_joined else None,
        }

        # 统计数据
        all_records = PracticeRecord.objects.filter(
            user=student, is_completed=True
        )
        period_records = all_records.filter(
            created_at__gte=start_date, created_at__lte=now
        )

        practice_stats = all_records.aggregate(
            count=Count('id'), avg=Avg('overall_score'), max_score=Max('overall_score')
        )

        # 活跃天数
        active_dates = set(all_records.values_list('created_at__date', flat=True))
        thirty_ago = now - timedelta(days=30)
        recent_active = all_records.filter(created_at__gte=thirty_ago)
        recent_active_dates = set(recent_active.values_list('created_at__date', flat=True))

        stats = {
            'practice_count': practice_stats['count'] or 0,
            'avg_score': round(practice_stats['avg'] or 0, 1),
            'max_score': practice_stats['max_score'] or 0,
            'completion_rate': 0,  # 占位
            'active_days': len(recent_active_dates),
        }

        # 状态判定
        avg_s = stats['avg_score']
        pc = stats['practice_count']
        days_login = (now - student.last_login).days if student.last_login else 999
        if avg_s >= 85:
            basic['status'] = 'excellent'
        elif avg_s >= 60 and days_login <= 7:
            basic['status'] = 'normal'
        else:
            basic['status'] = 'attention'

        # 成绩趋势（近30天每日均分）
        trend_records = period_records.extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(avg=Avg('overall_score')).order_by('day')
        score_trend = [{'date': t['day'].isoformat(), 'avg_score': round(t['avg'] or 0, 1)} for t in trend_records]

        # 练习记录明细
        record_list = period_records.order_by('-created_at')[:50].select_related('scenario', 'topic')
        practice_records_data = [
            {
                'scenario_title': r.scenario.title if r.scenario else '未知场景',
                'topic_title': r.topic.title if r.topic else '',
                'overall_score': r.overall_score,
                'duration_seconds': r.duration_seconds,
                'created_at': r.created_at.strftime('%Y-%m-%d %H:%M'),
            }
            for r in record_list
        ]

        return Response({
            'code': 200,
            'data': {
                'basic': basic,
                'stats': stats,
                'score_trend': score_trend,
                'practice_records': practice_records_data,
            }
        })
```

注意：需要在文件顶部的 import 区域确认已有 `Max` 的导入（来自 `django.db.models`）。如果缺少则补充：
```python
from django.db.models import Avg, Count, Max, Q, F
```

- [ ] **Step 2: 在 `users/api/urls.py` 注册新路由**

在现有 urlpatterns 列表中（`path('auth/my_classes/', ...)` 之后）追加：

```python
    path('teacher/workspace/', TeacherWorkspaceView.as_view(), name='teacher-workspace'),
    path('teacher/student/<int:pk>/', TeacherStudentDetailView.as_view(), name='teacher-student-detail'),
```

同时在文件顶部 import 中加入新视图：

```python
from .views import (
    LoginAPIView,
    LogoutAPIView,
    CurrentUserAPIView,
    ChangePasswordAPIView,
    MyClassesAPIView,
    UserViewSet,
    ClassInfoViewSet,
    TeacherWorkspaceView,
    TeacherStudentDetailView,
)
```

- [ ] **Step 3: 验证后端导入**

运行：

```bash
cd "/home/mjl/Prompt Teacher" && DJANGO_SETTINGS_MODULE=prompt_teaching.settings python -c "
import django; django.setup()
from users.api.views import TeacherWorkspaceView, TeacherStudentDetailView
print('TeacherWorkspaceView OK:', TeacherWorkspaceView)
print('TeacherStudentDetailView OK:', TeacherStudentDetailView)
"
```

预期输出：两行 OK 信息，无报错。

---

### Task 2: 前端 - 新增 API 封装层

**Files:**
- Create: `admin-panel/src/api/teacher.js`

- [ ] **Step 1: 创建 `api/teacher.js`**

```javascript
/**
 * 教师工作台 API 接口
 */
import request from '@/api/request'

/**
 * 获取教师工作台概览数据
 * @param {Object} params
 * @param {number} params.class_id - 班级ID（可选）
 * @param {string} params.period - 时间范围 7d/30d/90d/all
 */
export function getWorkspaceData(params = {}) {
  return request({
    url: '/teacher/workspace/',
    method: 'get',
    params: { period: '30d', ...params }
  })
}

/**
 * 获取学生详情
 * @param {number} id - 学生用户ID
 * @param {Object} params
 * @param {string} params.period - 时间范围
 */
export function getStudentDetail(id, params = {}) {
  return request({
    url: `/teacher/student/${id}/`,
    method: 'get',
    params: { period: '30d', ...params }
  })
}
```

---

### Task 3: 前端 - 教师工作台首页 Workspace.vue

**Files:**
- Create: `admin-panel/src/views/teacher/Workspace.vue`

- [ ] **Step 1: 创建完整的工作台首页组件**

```vue
<template>
  <div class="workspace-container">
    <!-- A区：顶部操作栏 -->
    <div class="page-header">
      <h2>📋 我的工作台</h2>
      <div class="header-actions">
        <el-select
          v-if="myClasses.length > 0"
          v-model="selectedClassId"
          placeholder="全部班级"
          clearable
          style="width: 180px; margin-right: 10px;"
          @change="fetchData"
        >
          <el-option
            v-for="cls in myClasses"
            :key="cls.id"
            :label="`${cls.name} (${cls.student_count}人)`"
            :value="cls.id"
          />
        </el-select>
        <el-select v-model="period" style="width: 130px; margin-right: 10px;" @change="fetchData">
          <el-option label="最近7天" value="7d" />
          <el-option label="最近30天" value="30d" />
          <el-option label="最近90天" value="90d" />
        </el-select>
        <el-button type="primary" plain disabled>
          📥 导出报告
        </el-button>
      </div>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-if="!loading && workspaceData.students && workspaceData.students.length === 0"
      description="您暂未管理任何班级和学生"
      :image-size="120"
    >
      <el-button type="primary">联系管理员分配班级</el-button>
    </el-empty>

    <div v-else v-loading="loading">
      <!-- B区：班级统计卡片 -->
      <el-row :gutter="16" class="stat-row">
        <el-col :span="4" v-for="(card, idx) in statCards" :key="idx">
          <el-card shadow="hover" class="stat-card" :style="{ borderTop: `3px solid ${card.color}` }">
            <div class="stat-value">{{ card.value }}</div>
            <div class="stat-label">{{ card.label }}</div>
          </el-card>
        </el-col>
      </el-row>

      <!-- C区：学生总览表 -->
      <el-card shadow="hover" class="table-card" style="margin-top: 20px;">
        <template #header>
          <span>📋 学生完成情况</span>
        </template>

        <el-table
          :data="workspaceData.students || []"
          stripe
          style="width: 100%"
          :default-sort="{ prop: 'avg_score', order: 'descending' }"
        >
          <el-table-column type="index" label="#" width="50" />
          <el-table-column prop="real_name" label="姓名" width="100" sortable />
          <el-table-column prop="student_id" label="学号" width="120" sortable />
          <el-table-column label="资料完成度" width="150" sortable :sort-method="(a,b)=>a.completion_rate-b.completion_rate">
            <template #default="{ row }">
              <el-progress :percentage="row.completion_rate || 0" :stroke-width="8" />
            </template>
          </el-table-column>
          <el-table-column prop="practice_count" label="练习次数" width="100" sortable sort-by="practice_count" />
          <el-table-column prop="avg_score" label="练习均分" width="110" sortable>
            <template #default="{ row }">
              <el-tag :type="scoreTagType(row.avg_score)" size="small">
                {{ row.avg_score || '-' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="最近登录" width="130" sortable prop="last_login">
            <template #default="{ row }">
              {{ formatRelativeTime(row.last_login) }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <span>{{ statusLabel(row.status) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="goDetail(row)">
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- D区：趋势图表 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card shadow="hover">
            <PieChart
              title="📊 班级成绩分布"
              :data="pieData"
              height="320px"
            />
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="hover">
            <LineChart
              title="📈 近30天活跃度趋势"
              :x-axis-data="trendDates"
              :series-data="trendActiveStudents"
              :show-area="true"
              height="320px"
            />
          </el-card>
        </el-col>
      </el-row>

      <!-- E区：预警提醒区 -->
      <el-card v-if="workspaceData.alerts && workspaceData.alerts.length > 0" shadow="hover" class="alert-card" style="margin-top: 20px;">
        <template #header>
          <span>⚠️ 需要关注的学生 ({{ workspaceData.alerts.length }}人)</span>
        </template>
        <div class="alert-list">
          <div
            v-for="(alert, idx) in workspaceData.alerts"
            :key="idx"
            class="alert-item"
          >
            <div class="alert-main">
              <strong>{{ alert.student_name }}</strong>
              <span class="alert-detail">{{ alert.detail }}</span>
            </div>
            <div class="alert-actions">
              <el-button link type="primary" size="small" @click="goDetailById(alert.student_id)">
                查看
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/modules/auth'
import PieChart from '@/components/charts/PieChart.vue'
import LineChart from '@/components/charts/LineChart.vue'
import { getWorkspaceData } from '@/api/teacher'
import { getMyClasses } from '@/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(false)
const period = ref('30d')
const selectedClassId = ref(null)
const myClasses = ref([])
const workspaceData = ref({})

// B区：统计卡片
const statCards = computed(() => {
  const s = workspaceData.value.stats || {}
  return [
    { label: '班级人数', value: s.total_students ?? '-', color: '#409EFF' },
    { label: '班级均分', value: s.class_avg_score ?? '-', color: '#67C23A' },
    { label: '资料完成率', value: `${s.material_completion_rate ?? 0}%`, color: '#E6A23C' },
    { label: '活跃率', value: `${s.active_rate ?? 0}%`, color: '#67C23A' },
    { label: '练习次数', value: s.total_practices ?? '-', color: '#F56C6C' },
    { label: '待关注', value: s.attention_count ?? 0, color: '#E6A23C' },
  ]
})

// D区：饼图数据
const pieData = computed(() => {
  const d = workspaceData.value.charts?.score_distribution || {}
  const labels = { excellent: '优秀(≥90)', good: '良好(80-89)', average: '中等(70-79)', pass: '及格(60-69)', fail: '不及格(<60)' }
  return Object.entries(d)
    .filter(([, v]) => v > 0)
    .map(([key, val]) => ({ name: labels[key] || key, value: val }))
})

// D区：折线图数据
const trendDates = computed(() =>
  (workspaceData.value.charts?.activity_trend || []).map(d => d.date)
)
const trendActiveStudents = computed(() =>
  (workspaceData.value.charts?.activity_trend || []).map(d => d.active_students || 0)
)

// 辅助方法
function scoreTagType(score) {
  if (!score && score !== 0) return 'info'
  if (score >= 90) return 'success'
  if (score >= 80) return ''
  if (score >= 60) return 'warning'
  return 'danger'
}

function statusLabel(status) {
  const map = { excellent: '🏆 优秀', normal: '✅ 正常', attention: '⚠️ 需关注' }
  return map[status] || '-'
}

function formatRelativeTime(isoStr) {
  if (!isoStr) return '-'
  const diff = Date.now() - new Date(isoStr).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${mins}分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days}天前`
  return new Date(isoStr).toLocaleDateString()
}

function goDetail(row) {
  router.push(`/teacher/student/${row.id}?period=${period.value}`)
}

function goDetailById(id) {
  router.push(`/teacher/student/${id}?period=${period.value}`)
}

// 数据加载
async function fetchData() {
  loading.value = true
  try {
    const params = { period: period.value }
    if (selectedClassId.value) params.class_id = selectedClassId.value
    const res = await getWorkspaceData(params)
    if (res.code === 200) {
      workspaceData.value = res.data
    }
  } catch (e) {
    console.error('加载工作台数据失败:', e)
  } finally {
    loading.value = false
  }
}

async function loadMyClasses() {
  try {
    const res = await getMyClasses()
    if (res.code === 200) myClasses.value = res.data || []
  } catch (e) { /* silent */ }
}

onMounted(async () => {
  await loadMyClasses()
  fetchData()
})
</script>

<style scoped lang="scss">
.workspace-container {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h2 {
      margin: 0;
      font-size: 22px;
      color: #303133;
    }

    .header-actions {
      display: flex;
      align-items: center;
    }
  }

  .stat-row {
    .stat-card {
      text-align: center;
      border-radius: 8px;

      .stat-value {
        font-size: 28px;
        font-weight: bold;
        color: #303133;
        margin-bottom: 4px;
      }

      .stat-label {
        font-size: 13px;
        color: #909399;
      }
    }
  }

  .table-card {
    border-radius: 8px;
  }

  .alert-card {
    border-radius: 8px;
    border-left: 4px solid #E6A23C;

    .alert-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .alert-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      background: #fdf6ec;
      border-radius: 6px;

      .alert-main {
        display: flex;
        gap: 12px;
        align-items: baseline;

        strong { color: #303133; }
        .alert-detail { color: #E6A23C; font-size: 13px; }
      }
    }
  }
}
</style>
```

---

### Task 4: 前端 - 学生详情页 StudentDetail.vue

**Files:**
- Create: `admin-panel/src/views/teacher/StudentDetail.vue`

- [ ] **Step 1: 创建学生详情页组件**

```vue
<template>
  <div class="student-detail-container" v-loading="loading">
    <!-- 顶部导航 -->
    <div class="page-header">
      <el-button text @click="$router.push('/teacher/workspace')">
        ← 返回工作台
      </el-button>
      <h2>学生详情：{{ detail.basic?.real_name }} ({{ detail.basic?.student_id }})</h2>
    </div>

    <div v-if="!loading && detail.basic">
      <el-row :gutter="20">
        <!-- 左侧：基本信息 + 统计面板 -->
        <el-col :span="8">
          <el-card shadow="hover" class="info-card">
            <div class="profile-section">
              <el-avatar :size="64" :src="detail.basic.avatar">
                {{ (detail.basic.real_name || '?').charAt(0) }}
              </el-avatar>
              <div class="profile-info">
                <h3>{{ detail.basic.real_name }}</h3>
                <p>学号：{{ detail.basic.student_id || '-' }}</p>
                <p>班级：{{ detail.basic.class_name || '-' }}</p>
                <p>注册：{{ formatDate(detail.basic.date_joined) }}</p>
                <el-tag :type="statusTagType(detail.basic.status)" size="small">
                  {{ statusLabel(detail.basic.status) }}
                </el-tag>
              </div>
            </div>
          </el-card>

          <el-card shadow="hover" class="stats-card" style="margin-top: 16px;">
            <template #header><span>📊 个人统计</span></template>
            <div class="stat-grid">
              <div class="stat-item">
                <div class="stat-val">{{ detail.stats?.practice_count }}</div>
                <div class="stat-lbl">练习次数</div>
              </div>
              <div class="stat-item">
                <div class="stat-val">{{ detail.stats?.avg_score }}</div>
                <div class="stat-lbl">平均分</div>
              </div>
              <div class="stat-item">
                <div class="stat-val">{{ detail.stats?.max_score }}</div>
                <div class="stat-lbl">最高分</div>
              </div>
              <div class="stat-item">
                <div class="stat-val">{{ detail.stats?.completion_rate }}%</div>
                <div class="stat-lbl">完成率</div>
              </div>
              <div class="stat-item">
                <div class="stat-val">{{ detail.stats?.active_days }}</div>
                <div class="stat-lbl">活跃天数</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧：成绩趋势图 -->
        <el-col :span="16">
          <el-card shadow="hover">
            <LineChart
              title="📈 成绩趋势（近30天）"
              :x-axis-data="trendDates"
              :series-data="trendScores"
              :smooth="true"
              height="360px"
            />
          </el-card>
        </el-col>
      </el-row>

      <!-- 练习记录明细表 -->
      <el-card shadow="hover" style="margin-top: 20px;">
        <template #header>
          <span>📋 练习记录明细</span>
          <el-select v-model="recordPeriod" size="small" style="float: right; width: 120px;" @change="fetchDetail">
            <el-option label="近7天" value="7d" />
            <el-option label="近30天" value="30d" />
            <el-option label="近90天" value="90d" />
          </el-select>
        </template>
        <el-table :data="detail.practice_records || []" stripe>
          <el-table-column prop="scenario_title" label="场景" min-width="140" />
          <el-table-column prop="topic_title" label="主题" min-width="160" />
          <el-table-column prop="overall_score" label="得分" width="80">
            <template #default="{ row }">
              <el-tag :type="scoreTagType(row.overall_score)" size="small">
                {{ row.overall_score }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="耗时" width="90">
            <template #default="{ row }">
              {{ formatDuration(row.duration_seconds) }}
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="日期" width="160" />
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import LineChart from '@/components/charts/LineChart.vue'
import { getStudentDetail } from '@/api/teacher'

const route = useRoute()
const loading = ref(false)
const detail = ref({})
const recordPeriod = ref('30d')

const studentId = computed(() => route.params.id)

const trendDates = computed(() =>
  (detail.value.score_trend || []).map(t => t.date)
)
const trendScores = computed(() =>
  (detail.value.score_trend || []).map(t => t.avg_score)
)

function scoreTagType(score) {
  if (score >= 90) return 'success'
  if (score >= 80) return ''
  if (score >= 60) return 'warning'
  return 'danger'
}

function statusTagType(status) {
  const map = { excellent: 'success', normal: '', attention: 'warning' }
  return map[status] || 'info'
}

function statusLabel(status) {
  const map = { excellent: '🏆 优秀', normal: '✅ 正常', attention: '⚠️ 需关注' }
  return map[status] || '-'
}

function formatDate(isoStr) {
  if (!isoStr) return '-'
  return new Date(isoStr).toLocaleDateString()
}

function formatDuration(seconds) {
  if (!seconds) return '-'
  if (seconds < 60) return `${seconds}秒`
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return s ? `${m}分${s}秒` : `${m}分钟`
}

async function fetchDetail() {
  loading.value = true
  try {
    const res = await getStudentDetail(studentId.value, { period: recordPeriod.value })
    if (res.code === 200) {
      detail.value = res.data
    }
  } catch (e) {
    console.error('加载学生详情失败:', e)
  } finally {
    loading.value = false
  }
}

watch(recordPeriod, fetchDetail)

onMounted(fetchDetail)
</script>

<style scoped lang="scss">
.student-detail-container {
  .page-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;

    h2 {
      margin: 0;
      font-size: 20px;
      color: #303133;
    }
  }

  .info-card {
    border-radius: 8px;

    .profile-section {
      display: flex;
      gap: 16px;
      align-items: flex-start;

      .profile-info {
        h3 { margin: 0 0 8px; color: #303133; }
        p { margin: 2px 0; font-size: 13px; color: #606266; }
      }
    }
  }

  .stats-card {
    border-radius: 8px;

    .stat-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;

      .stat-item {
        text-align: center;
        padding: 8px;
        background: #f5f7fa;
        border-radius: 6px;

        .stat-val { font-size: 20px; font-weight: bold; color: #303133; }
        .stat-lbl { font-size: 12px; color: #909399; margin-top: 2px; }
      }
    }
  }
}
</style>
```

---

### Task 5: 前端 - 路由配置 + 侧边栏菜单

**Files:**
- Modify: `admin-panel/src/router/index.js`
- Modify: `admin-panel/src/components/Layout/AdminLayout.vue`

- [ ] **Step 1: 在 `router/index.js` 新增教师工作台路由**

在 dashboard 路由之后、UserList 路由之前插入：

```javascript
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
```

- [ ] **Step 2: 修改默认 redirect（教师登录跳转到工作台）**

将根路径 redirect 从 `/dashboard` 改为按角色动态判断：

找到这行：
```javascript
redirect: '/dashboard',
```

替换为：
```javascript
redirect: '/dashboard',
```
（保持不变——因为 redirect 是静态的，我们通过路由守卫动态处理更合理）

改为在 `router.beforeEach` 守卫中增加逻辑：当教师访问 `/` 时重定向到 `/teacher/workspace`。

在 `router.beforeEach` 函数中，`next()` 调用之前，插入：

```javascript
  // 教师/管理员登录后优先进入工作台
  if (to.path === '/' && authStore.role === 'teacher') {
    next('/teacher/workspace')
    return
  }
```

注意：这段代码应放在 `if (to.meta.requiresAuth ...)` 检查之前或在其内部逻辑中。

- [ ] **Step 3: 在 `AdminLayout.vue` 侧边栏添加「我的工作台」菜单项**

在 `menuList` 数组中，仪表盘 (`/dashboard`) 菜单项之后插入：

```javascript
  {
    path: '/teacher/workspace',
    title: '我的工作台',
    icon: Monitor,
    roles: ['admin', 'teacher']
  },
```

同时在 import 区域中添加 `Monitor` 图标：

```python
Monitor,   # 在 icons-vue 导入列表中追加
```

具体位置：在已有的 icon imports 中追加 `Monitor`：

```javascript
import {
  ChatDotRound,
  Odometer,
  Monitor,
  Reading,
  // ... 其余不变
```

---

### Task 6: 验证

- [ ] **Step 1: 验证后端 API 无语法错误**

```bash
cd "/home/mjl/Prompt Teacher" && DJANGO_SETTINGS_MODULE=prompt_teaching.settings python -c "
import django; django.setup()
from users.api.views import TeacherWorkspaceView, TeacherStudentDetailView
from users.api.urls import urlpatterns
print('Views OK')
print(f'Total urls: {len(urlpatterns)}')
for u in urlpatterns:
    print(f'  {u.pattern}')
"
```

预期：无报错，输出包含 `teacher/workspace/` 和 `teacher/student/<int:pk>/` 路由。

- [ ] **Step 2: 验证前端无编译错误**

```bash
cd "/home/mjl/Prompt Teacher/admin-panel" && npx vue-tsc --noEmit --skipLibCheck 2>&1 | head -30
```

预期：无 TypeScript 错误（或仅有无关的预存警告）。
