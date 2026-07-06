"""
数据分析服务基类
提供缓存、权限控制等通用功能
"""

from django.core.cache import cache
from functools import wraps
from datetime import timedelta
from django.utils import timezone


def cache_analytics_result(timeout=300):
    """
    缓存装饰器 - 自动缓存分析结果
    
    Args:
        timeout: 缓存过期时间(秒)，默认5分钟
    
    使用示例:
        @cache_analytics_result(timeout=600)
        def get_statistics(self, user_id, period):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"analytics:{func.__name__}:{hash(frozenset(kwargs.items()))}"
            
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            result = func(*args, **kwargs)
            
            if result is not None:
                cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


class BaseAnalyticsService:
    """
    数据分析服务基类
    
    提供通用的数据聚合、时间处理、权限过滤等功能
    """
    
    PERIOD_MAP = {
        '7d': 7,
        '30d': 30,
        '90d': 90,
        'all': None  # 全部时间
    }
    
    @classmethod
    def get_time_range(cls, period='30d'):
        """
        根据period参数获取时间范围
        
        Args:
            period: 时间范围 (7d/30d/90d/all)
        
        Returns:
            tuple: (start_date, end_date) 或 (None, None)表示全部
        """
        days = cls.PERIOD_MAP.get(period, 30)
        
        if days is None:
            return (None, None)
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        return (start_date, end_date)
    
    @classmethod
    def filter_by_role(cls, queryset, user):
        """
        根据用户角色过滤数据集
        
        Args:
            queryset: 原始QuerySet
            user: 当前用户实例
        
        Returns:
            QuerySet: 过滤后的数据集
        """
        if not user.is_authenticated:
            return queryset.none()
        
        role = getattr(user, 'role', 'student')
        
        if role == 'student':
            # 学生只能看到自己的数据
            if hasattr(queryset.model, 'user'):
                return queryset.filter(user=user)
            elif hasattr(queryset.model, 'user_id'):
                return queryset.filter(user_id=user.id)
        
        elif role == 'teacher':
            # 教师只能看到自己管理的学生数据
            from users.models import UserProfile

            managed_student_ids = UserProfile.objects.filter(
                teacher=user
            ).values_list('pk', flat=True)

            if not managed_student_ids:
                return queryset.none()

            model = queryset.model
            if model == UserProfile:
                return queryset.filter(pk__in=managed_student_ids)
            if hasattr(model, 'user') or hasattr(model, 'user_id'):
                return queryset.filter(user_id__in=managed_student_ids)
            try:
                return queryset.filter(user_id__in=managed_student_ids)
            except Exception:
                return queryset
        
        # 管理员可以看到所有数据
        return queryset

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

    @classmethod
    def safe_divide(cls, numerator, denominator, default=0):
        """
        安全除法，避免除零错误
        
        Args:
            numerator: 分子
            denominator: 分母
            default: 除零时的默认值
        
        Returns:
            float: 计算结果或默认值
        """
        if denominator == 0:
            return default
        return round(numerator / denominator * 100, 1) if default > 1 else round(numerator / denominator, 2)
    
    @classmethod
    def calculate_trend(cls, current, previous):
        """
        计算变化趋势
        
        Args:
            current: 当前值
            previous: 前一个值
        
        Returns:
            dict: {'direction': 'up'/'down'/'stable', 'value': 百分比}
        """
        if previous == 0:
            return {'direction': 'stable', 'value': 0}
        
        change = ((current - previous) / previous) * 100
        
        if change > 1:
            direction = 'up'
        elif change < -1:
            direction = 'down'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'value': round(change, 1)
        }
    
    @staticmethod
    def clear_cache(prefix='analytics'):
        """
        清除所有分析缓存 (谨慎使用)
        
        Args:
            prefix: 缓存键前缀
        """
        # 注意：Django的cache backend不支持按前缀批量删除
        # 这里仅作为接口预留，实际实现取决于具体缓存后端
        pass
