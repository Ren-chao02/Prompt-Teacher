from django.db import models
from django.utils.deprecation import MiddlewareMixin


class DataPermissionMiddleware(MiddlewareMixin):
    """
    数据权限中间件 - 自动根据用户角色过滤 QuerySet
    
    功能:
    1. 为 request.user 添加 get_filtered_queryset() 方法
    2. 根据角色自动过滤:
       - admin: 返回全部数据
       - teacher: 返回自己 + 自己的学生数据
       - student: 仅返回自己的数据
    
    使用方法:
    # 在 ViewSet 中调用
    def get_queryset(self):
        return self.request.user.get_filtered_queryset(self.queryset_model)
    """

    def process_request(self, request):
        """为用户对象添加数据权限方法"""
        
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return
        
        user = request.user
        
        def get_filtered_queryset(model_class, base_queryset=None):
            """
            获取经过权限过滤的 QuerySet
            
            Args:
                model_class: Django 模型类 (如 UserProfile, PracticeRecord)
                base_queryset: 基础查询集（可选）
            
            Returns:
                过滤后的 QuerySet
            """
            
            if base_queryset is None:
                queryset = model_class.objects.all()
            else:
                queryset = base_queryset
            
            role = getattr(user, 'role', None)
            
            if role == 'admin':
                return queryset
            
            elif role == 'teacher':
                return self._filter_for_teacher(user, queryset, model_class)
            
            elif role == 'student':
                return self._filter_for_student(user, queryset, model_class)
            
            else:
                return queryset.none()
        
        def can_access_object(obj):
            """
            检查用户是否有权访问某个对象实例
            
            Args:
                obj: 模型实例
            
            Returns:
                bool: 是否有访问权限
            """
            
            role = getattr(user, 'role', None)
            
            if role == 'admin':
                return True
            
            elif role == 'teacher':
                if isinstance(obj, user.__class__):
                    return obj.pk == user.pk or obj.teacher_id == user.pk
                
                if hasattr(obj, 'user'):
                    obj_user = obj.user
                    return (
                        obj_user.pk == user.pk or 
                        getattr(obj_user, 'teacher_id', None) == user.pk
                    )
                
                if hasattr(obj, 'teacher') and obj.teacher:
                    return obj.teacher.pk == user.pk
                
                return False
            
            elif role == 'student':
                if isinstance(obj, user.__class__):
                    return obj.pk == user.pk
                
                if hasattr(obj, 'user'):
                    return obj.user.pk == user.pk
                
                return False
            
            return False
        
        # 将方法绑定到用户对象
        user.get_filtered_queryset = get_filtered_queryset
        user.can_access_object = can_access_object

    def _filter_for_teacher(self, user, queryset, model_class):
        """教师角色：返回自己 + 自己的学生"""
        
        from users.models import UserProfile
        
        if model_class == UserProfile:
            return queryset.filter(
                models.Q(pk=user.pk) | models.Q(teacher=user)
            )
        
        if hasattr(model_class, 'user'):
            student_ids = UserProfile.objects.filter(
                teacher=user
            ).values_list('pk', flat=True)
            
            return queryset.filter(
                models.Q(user_id__in=student_ids) | models.Q(user_id=user.pk)
            )
        
        if hasattr(model_class, 'teacher'):
            return queryset.filter(teacher=user)
        
        return queryset.filter(user=user)

    def _filter_for_student(self, user, queryset, model_class):
        """学生角色：仅返回自己的数据"""
        
        from users.models import UserProfile
        
        if model_class == UserProfile:
            return queryset.filter(pk=user.pk)
        
        if hasattr(model_class, 'user'):
            return queryset.filter(user=user)
        
        return queryset.none()
