"""
数据分析 API 视图
提供概览、学习进度、练习统计等接口
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Sum, Max, Q
from django.utils import timezone
from datetime import timedelta

from learning.models import LearningMaterial
from practice.models import PracticeScenario, PracticeTopic, PracticeRecord
from users.models import UserProfile

from .serializers import (
    OverviewResponseSerializer,
    LearningProgressResponseSerializer,
    PracticeStatisticsResponseSerializer
)
from ..services.base_analytics import BaseAnalyticsService


class AnalyticsViewSet(viewsets.GenericViewSet):
    """
    数据分析 ViewSet
    
    list: 数据概览 (平台核心指标)
    learning_progress: 学习进度分析
    practice_statistics: 练习成绩统计
    export: 导出数据 (Excel/PDF)
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        获取数据概览
        
        查询参数:
            period: 时间范围 (7d/30d/90d)，默认30d
        
        返回:
            学习、练习、用户三大模块的核心指标
            热门内容排行、优秀学员(权限控制)
        """
        user = request.user
        period = request.query_params.get('period', '30d')
        
        start_date, end_date = BaseAnalyticsService.get_time_range(period)
        
        data = {
            'learning': self._get_learning_overview(start_date, end_date),
            'practice': self._get_practice_overview(start_date, end_date),
            'users': self._get_user_overview(start_date, end_date),
            'daily_trend': self._get_daily_trend(start_date, end_date),
            'top_content': self._get_top_content(limit=10),
        }
        
        # 权限控制：只有管理员和教师可以看到优秀学员排行
        role = getattr(user, 'role', 'student')
        if role in ['admin', 'teacher']:
            data['top_users'] = self._get_top_users(limit=10)
        
        serializer = OverviewResponseSerializer(data)
        return Response({
            'code': 200,
            'message': '获取数据概览成功',
            'data': serializer.data
        })
    
    def _get_learning_overview(self, start_date=None, end_date=None):
        """获取学习模块概览数据"""
        base_qs = LearningMaterial.objects.all()
        
        total_materials = base_qs.count()
        
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_new = base_qs.filter(created_at__gte=today_start).count()
        
        # 计算完成率 (使用已发布资料的比例作为近似)
        published_count = base_qs.filter(status='published').count()
        completion_rate = BaseAnalyticsService.safe_divide(
            published_count, total_materials, default=0
        )
        
        # 平均阅读时长 (分钟) - 使用LearningMaterial的reading_time属性
        materials = list(base_qs.only('content'))
        if materials:
            total_reading_time = sum([m.reading_time for m in materials])
            avg_read_time = round(total_reading_time / len(materials), 1)
        else:
            avg_read_time = 0
        
        return {
            'total_materials': total_materials,
            'today_new': today_new,
            'completion_rate': completion_rate,
            'avg_read_time': avg_read_time
        }
    
    def _get_practice_overview(self, start_date=None, end_date=None):
        """获取练习模块概览数据"""
        base_qs = PracticeRecord.objects.all()
        
        if start_date and end_date:
            base_qs = base_qs.filter(created_at__range=[start_date, end_date])
        
        total_records = base_qs.count()
        
        # 平均分
        avg_score_result = base_qs.aggregate(
            avg=Avg('overall_score')
        )
        avg_score = round(avg_score_result['avg'] or 0, 1)
        
        # 通过率 (>=60分视为通过)
        pass_count = base_qs.filter(overall_score__gte=60).count()
        pass_rate = BaseAnalyticsService.safe_divide(
            pass_count, total_records, default=0
        )
        
        return {
            'total_records': total_records,
            'avg_score': avg_score,
            'pass_rate': pass_rate
        }
    
    def _get_user_overview(self, start_date=None, end_date=None):
        """获取用户统计数据"""
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = timezone.now() - timedelta(days=7)
        
        # 今日活跃用户 (有登录或有操作记录)
        active_today = UserProfile.objects.filter(
            last_login__gte=today_start
        ).count()
        
        # 本周新增用户
        new_this_week = UserProfile.objects.filter(
            date_joined__gte=week_ago
        ).count()
        
        # 留存率 (简化计算：7天前注册且今天还登录的用户 / 7天前注册的总用户)
        retention_base = UserProfile.objects.filter(
            date_joined__lte=week_ago
        )
        retained_count = retention_base.filter(
            last_login__gte=today_start
        ).count()
        
        retention_total = retention_base.count()
        retention_rate = BaseAnalyticsService.safe_divide(
            retained_count, retention_total, default=0
        )
        
        return {
            'active_today': active_today,
            'new_this_week': new_this_week,
            'retention_rate': retention_rate
        }
    
    def _get_daily_trend(self, start_date=None, end_date=None):
        """获取每日趋势数据"""
        days = BaseAnalyticsService.PERIOD_MAP.get('30d', 30)
        if start_date and end_date:
            days = (end_date - start_date).days
        
        trend_data = []
        current_date = (end_date or timezone.now()).date()
        
        for i in range(min(days, 30), 0, -1):
            day = current_date - timedelta(days=i)
            day_start = timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.min.time()))
            day_end = day_start + timedelta(days=1)
            
            # 当日新增学习资料数
            material_count = LearningMaterial.objects.filter(
                created_at__range=[day_start, day_end]
            ).count()
            
            # 当日练习记录数
            practice_count = PracticeRecord.objects.filter(
                created_at__range=[day_start, day_end]
            ).count()
            
            trend_data.append({
                'date': day.isoformat(),
                'value': material_count + practice_count,
                'count': material_count + practice_count
            })
        
        return trend_data
    
    def _get_top_content(self, limit=10):
        """获取热门内容排行"""
        top_content = LearningMaterial.objects.filter(
            status='published'
        ).order_by('-view_count', '-like_count')[:limit].values(
            'id', 'title', 'category', 'view_count', 'like_count'
        )
        
        result = []
        for item in top_content:
            result.append({
                **item,
                'views': item['view_count'],
                'completions': item['like_count']  # 用点赞数近似完成数
            })
        
        return result
    
    def _get_top_users(self, limit=10):
        """获取优秀学员排行 (仅Admin/Teacher可见)"""
        top_users = UserProfile.objects.annotate(
            total_practices=Count('practice_records'),
            avg_score=Avg('practice_records__overall_score')
        ).filter(
            total_practices__gt=0
        ).order_by('-avg_score', '-total_practices')[:limit].values(
            'id', 'username', 'role', 'total_practices', 'avg_score'
        )
        
        # 格式化平均分
        for user in top_users:
            user['avg_score'] = round(user['avg_score'] or 0, 1)
        
        return list(top_users)

    @action(detail=False, methods=['get'])
    def learning_progress(self, request):
        """
        学习进度分析
        
        查询参数:
            user_id: 用户ID (可选，不传则看全局)
            period: 时间范围 (7d/30d/90d/all)
            category: 内容分类筛选
        
        返回:
            学习时间线、完成情况、热门内容、学习习惯
        """
        user = request.user
        user_id = request.query_params.get('user_id')
        period = request.query_params.get('period', '30d')
        category = request.query_params.get('category')
        
        start_date, end_date = BaseAnalyticsService.get_time_range(period)
        
        # 权限控制：学生只能看自己的数据
        target_user_id = user_id
        if getattr(user, 'role', '') == 'student':
            target_user_id = str(user.id)
        
        data = {
            'timeline': self._get_learning_timeline(target_user_id, start_date, end_date),
            'completion': self._get_completion_stats(target_user_id, category),
            'popular_content': self._get_popular_by_category(category, limit=10),
            'reading_habits': self._get_reading_habits(target_user_id)
        }
        
        serializer = LearningProgressResponseSerializer(data)
        return Response({
            'code': 200,
            'message': '获取学习进度成功',
            'data': serializer.data
        })
    
    def _get_learning_timeline(self, user_id, start_date=None, end_date=None):
        """获取学习时间线数据 - 使用LearningMaterial的创建时间和阅读量"""
        base_qs = LearningMaterial.objects.all()
        
        if user_id:
            # 如果指定用户，只看该用户创建的资料（或后续添加作者过滤）
            base_qs = base_qs.filter(author_id=user_id)
        
        if start_date and end_date:
            base_qs = base_qs.filter(created_at__range=[start_date, end_date])
        
        # 按天聚合学习资料创建情况
        timeline = base_qs.dates('created_at', 'day').annotate(
            read_minutes=Sum('view_count') / 60,  # 用总阅读量近似
            completed_count=Count('id', filter=Q(status='published'))
        ).order_by('created_at').values_list(
            'created_at', 'read_minutes', 'completed_count'
        )
        
        dates = []
        read_minutes = []
        completed_count = []
        
        for item in timeline:
            dates.append(str(item[0]))
            read_minutes.append(int(item[1] or 0))
            completed_count.append(item[2] or 0)
        
        return {
            'dates': dates,
            'read_minutes': read_minutes,
            'completed_count': completed_count
        }
    
    def _get_completion_stats(self, user_id=None, category=None):
        """获取完成率统计 - 基于资料发布状态"""
        materials = LearningMaterial.objects.all()
        
        if category:
            materials = materials.filter(category=category)
        
        total = materials.count()
        
        # 已发布的材料视为"已完成"
        published_ids = set(materials.filter(status='published').values_list('id', flat=True))
        
        by_category = {}
        for material in materials:
            cat = material.category or '未分类'
            if cat not in by_category:
                by_category[cat] = {'total': 0, 'completed': 0}
            by_category[cat]['total'] += 1
            if material.id in published_ids:
                by_category[cat]['completed'] += 1
        
        # 计算每个分类的完成率
        for cat, stats in by_category.items():
            stats['rate'] = BaseAnalyticsService.safe_divide(
                stats['completed'], stats['total']
            )
        
        overall_completed = len(published_ids)
        overall_rate = BaseAnalyticsService.safe_divide(overall_completed, total)
        
        return {
            'by_category': by_category,
            'overall_rate': overall_rate
        }
    
    def _get_popular_by_category(self, category=None, limit=10):
        """按分类获取热门内容"""
        qs = LearningMaterial.objects.filter(status='published')
        
        if category:
            qs = qs.filter(category=category)
        
        popular = qs.order_by('-view_count', '-like_count')[:limit].values(
            'id', 'title', 'view_count', 'like_count'
        )
        
        result = []
        for item in popular:
            result.append({
                **item,
                'views': item['view_count'],
                'completions': item['like_count']
            })
        
        return result
    
    def _get_reading_habits(self, user_id=None):
        """分析学习习惯 - 基于LearningMaterial的创建时间"""
        base_qs = LearningMaterial.objects.all()
        
        if user_id:
            base_qs = base_qs.filter(author_id=user_id)
        
        habits = {}
        
        # 高峰时段分析 (简化版：取最近100条记录的小时分布)
        recent_materials = base_qs.order_by('-created_at')[:100]
        hour_counts = [0] * 24
        for material in recent_materials:
            hour = material.created_at.hour
            hour_counts[hour] += 1
        
        # 找出Top3高峰时段
        hour_with_counts = [(h, c) for h, c in enumerate(hour_counts) if c > 0]
        hour_with_counts.sort(key=lambda x: x[1], reverse=True)
        peak_hours = [h[0] for h in hour_with_counts[:3]]
        
        habits['peak_hours'] = peak_hours
        
        # 平均阅读时长 (使用reading_time属性)
        materials = list(base_qs.only('content'))
        if materials:
            total_reading_time = sum([m.reading_time for m in materials])
            habits['avg_session_duration'] = round(total_reading_time / len(materials), 1)
        else:
            habits['avg_session_duration'] = 0
        
        # 偏好分类
        category_counts = base_qs.values('category').annotate(count=Count('id')).order_by('-count')[:5]
        preferred = [c['category'] for c in category_counts if c['category']]
        habits['preferred_categories'] = preferred
        
        # 每周活跃天数 (简化版：基于资料创建日期)
        unique_days = base_qs.dates('created_at', 'day').count()
        habits['active_days_sample'] = min(unique_days, 7)  # 样本期内活跃天数
        
        return habits

    @action(detail=False, methods=['get'])
    def practice_statistics(self, request):
        """
        练习成绩统计分析
        
        查询参数:
            user_id: 用户ID (可选)
            scenario_id: 场景ID (可选)
            score_level: 分数等级筛选 (excellent/good/average/fail)
            period: 时间范围 (7d/30d/90d)
        
        返回:
            成绩趋势、分数分布、场景对比、薄弱点识别、排行榜
        """
        user = request.user
        user_id = request.query_params.get('user_id')
        scenario_id = request.query_params.get('scenario_id')
        score_level = request.query_params.get('score_level')
        period = request.query_params.get('period', '30d')
        
        start_date, end_date = BaseAnalyticsService.get_time_range(period)
        
        # 权限控制
        target_user_id = user_id
        if getattr(user, 'role', '') == 'student':
            target_user_id = str(user.id)
        
        data = {
            'score_trend': self._get_score_trend(target_user_id, scenario_id, start_date, end_date),
            'distribution': self._get_score_distribution(target_user_id, scenario_id, score_level),
            'scenario_comparison': self._get_scenario_comparison(target_user_id),
            'weak_points': self._identify_weak_points(target_user_id)
        }
        
        # 排行榜仅对管理员和教师可见
        role = getattr(user, 'role', '')
        if role in ['admin', 'teacher']:
            data['ranking'] = self._get_practice_ranking(scenario_id, limit=20)
        
        serializer = PracticeStatisticsResponseSerializer(data)
        return Response({
            'code': 200,
            'message': '获取练习统计成功',
            'data': serializer.data
        })
    
    def _get_score_trend(self, user_id=None, scenario_id=None, start_date=None, end_date=None):
        """获取成绩趋势"""
        base_qs = PracticeRecord.objects.all()
        
        if user_id:
            base_qs = base_qs.filter(user_id=user_id)
        if scenario_id:
            base_qs = base_qs.filter(scenario_id=scenario_id)
        if start_date and end_date:
            base_qs = base_qs.filter(created_at__range=[start_date, end_date])
        
        trend = base_qs.dates('created_at', 'day').annotate(
            avg_score=Avg('overall_score'),
            count=Count('id')
        ).order_by('created_at').values_list(
            'created_at', 'avg_score', 'count'
        )
        
        dates = []
        scores = []
        
        for item in trend:
            dates.append(str(item[0]))
            scores.append(round(item[1] or 0, 1))
        
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            'dates': dates,
            'scores': scores,
            'avg_score': round(avg_score, 1)
        }
    
    def _get_score_distribution(self, user_id=None, scenario_id=None, score_level=None):
        """获取分数分布"""
        base_qs = PracticeRecord.objects.all()
        
        if user_id:
            base_qs = base_qs.filter(user_id=user_id)
        if scenario_id:
            base_qs = base_qs.filter(scenario_id=scenario_id)
        if score_level:
            base_qs = base_qs.filter(score_level=score_level)
        
        all_scores = list(base_qs.values_list('overall_score', flat=True))
        
        distribution = {
            'excellent': len([s for s in all_scores if 90 <= s <= 100]),
            'good': len([s for s in all_scores if 80 <= s < 90]),
            'average': len([s for s in all_scores if 70 <= s < 80]),
            'below_average': len([s for s in all_scores if 60 <= s < 70]),
            'fail': len([s for s in all_scores if 0 <= s < 60])
        }
        
        if all_scores:
            sorted_scores = sorted(all_scores)
            n = len(sorted_scores)
            
            distribution['mean'] = round(sum(all_scores) / n, 1)
            distribution['median'] = round(sorted_scores[n // 2], 1)
            
            if n > 1:
                mean = sum(all_scores) / n
                variance = sum((x - mean) ** 2 for x in all_scores) / (n - 1)
                distribution['std_dev'] = round(variance ** 0.5, 1)
            else:
                distribution['std_dev'] = 0.0
        else:
            distribution['mean'] = 0.0
            distribution['median'] = 0.0
            distribution['std_dev'] = 0.0
        
        return distribution
    
    def _get_scenario_comparison(self, user_id=None):
        """各场景表现对比"""
        base_qs = PracticeRecord.objects.all()
        
        if user_id:
            base_qs = base_qs.filter(user_id=user_id)
        
        comparison = base_qs.values('scenario__id', 'scenario__title', 'scenario__icon', 'scenario__difficulty').annotate(
            avg_score=Avg('overall_score'),
            practice_count=Count('id'),
            best_score=Max('overall_score')
        ).filter(practice_count__gt=0).order_by('-avg_score')
        
        result = []
        for item in comparison:
            result.append({
                'scenario_id': item['scenario__id'],
                'scenario_title': item['scenario__title'],
                'icon': item['scenario__icon'] or '📊',
                'difficulty': item['scenario__difficulty'] or 'intermediate',
                'avg_score': round(item['avg_score'] or 0, 1),
                'practice_count': item['practice_count'],
                'best_score': round(item['best_score'] or 0, 1),
                'improvement_rate': ''  # TODO: 实现历史对比逻辑
            })
        
        return result[:10]  # Top 10 场景
    
    def _identify_weak_points(self, user_id=None):
        """识别薄弱知识点"""
        base_qs = PracticeRecord.objects.all()
        
        if user_id:
            base_qs = base_qs.filter(user_id=user_id)
        
        topic_stats = base_qs.values('topic__id', 'topic__title').annotate(
            total_attempts=Count('id'),
            avg_score=Avg('overall_score'),
            low_score_count=Count('id', filter=Q(overall_score__lt=60))
        ).filter(total_attempts__gte=3).order_by('avg_score')
        
        weak_points = []
        for stat in topic_stats[:10]:
            error_rate = BaseAnalyticsService.safe_divide(
                stat['low_score_count'], stat['total_attempts']
            )
            
            if error_rate > 30 or (stat['avg_score'] and stat['avg_score'] < 70):
                weak_points.append({
                    'topic_id': stat['topic__id'],
                    'topic_title': stat['topic__title'] or '未知主题',
                    'error_rate': error_rate,
                    'total_attempts': stat['total_attempts'],
                    'suggestion': f"建议加强'{stat['topic__title']}'的练习"
                })
        
        return weak_points
    
    def _get_practice_ranking(self, scenario_id=None, limit=20):
        """练习排行榜"""
        base_qs = UserProfile.objects.annotate(
            total_practices=Count('practice_records'),
            avg_score=Avg('practice_records__overall_score'),
            best_score=Max('practice_records__overall_score')
        ).filter(total_practices__gt=0)
        
        if scenario_id:
            base_qs = base_qs.filter(
                practice_records__scenario_id=scenario_id
            )
        
        ranking = base_qs.order_by('-avg_score', '-total_practices')[:limit].values(
            'id', 'username', 'avatar', 'total_practices', 'avg_score', 'best_score'
        )
        
        result = []
        for rank, user in enumerate(ranking, 1):
            result.append({
                'id': user['id'],
                'username': user['username'],
                'role': getattr(user, 'role', ''),
                'total_practices': user['total_practices'],
                'avg_score': round(user['avg_score'] or 0, 1)
            })
        
        return result

    @action(detail=False, methods=['post'])
    def export(self, request):
        """
        导出数据分析结果
        
        请求体:
            format: 导出格式 (excel/csv/pdf)
            type: 数据类型 (overview/learning/practice)
            filters: 筛选条件
        
        返回:
            文件下载流
        """
        format_type = request.data.get('format', 'excel')
        export_type = request.data.get('type', 'overview')
        filters = request.data.get('filters', {})
        
        # TODO: 实现导出逻辑
        # 使用 pandas/openpyxl 生成 Excel
        # 使用 reportlab/weasyprint 生成 PDF
        
        return Response({
            'code': 200,
            'message': f'导出功能开发中，当前支持格式: {format_type}',
            'data': {
                'download_url': None,
                'expires_in': 3600
            }
        }, status=status.HTTP_200_OK)
