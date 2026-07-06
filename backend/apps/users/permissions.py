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


class IsStudentOrAbove(permissions.BasePermission):
    """所有认证用户可访问"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    自定义权限 - 仅对象所有者可以编辑
    其他用户只能读取 (SAFE_METHODS: GET, HEAD, OPTIONS)
    """
    message = '只有所有者才能修改此资源'
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 检查对象是否属于当前用户
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        # 如果是 UserProfile 对象本身
        if hasattr(obj, 'pk'):
            return obj.pk == request.user.pk
        
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """管理员可读写，其他用户只读"""
    message = '只有管理员才能执行写操作'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return getattr(request.user, 'role', None) == 'admin'


class DynamicRolePermission(permissions.BasePermission):
    """
    动态角色权限 - 根据视图 action 动态判断
    
    使用方法:
    class UserViewSet(viewsets.ModelViewSet):
        permission_classes = [DynamicRolePermission]
        
        role_permissions = {
            'list': ['admin', 'teacher'],
            'create': ['admin'],
            'retrieve': ['admin', 'teacher', 'student'],
            'update': ['admin'],
            'destroy': ['admin']
        }
    """
    
    def get_required_roles(self, view):
        """获取当前 action 所需的角色列表"""
        action = getattr(view, 'action', None)
        role_permissions = getattr(view, 'role_permissions', {})
        return role_permissions.get(action, [])
    
    def has_permission(self, request, view):
        required_roles = self.get_required_roles(view)
        
        # 如果没有配置角色要求，默认允许认证用户
        if not required_roles:
            return request.user.is_authenticated
        
        user_role = getattr(request.user, 'role', None)
        
        if not request.user.is_authenticated:
            return False
        
        if user_role not in required_roles:
            allowed_roles_str = ', '.join(required_roles)
            self.message = f'需要 {allowed_roles_str} 权限，当前角色: {user_role or "未设置"}'
            return False
        
        return True


class ActionBasedPermission(permissions.BasePermission):
    """
    基于 action 的细粒度权限控制
    
    示例配置:
    class MyViewSet(viewsets.ModelViewSet):
        permission_classes = [ActionBasedPermission]
        
        # action -> 权限类映射
        action_permissions = {
            'list': [IsAuthenticated],
            'create': [IsAdmin],
            'update': [IsAdmin | IsOwner],
            'destroy': [IsAdmin]
        }
    """
    
    def get_action_permissions(self, view):
        """获取当前 action 的权限类列表"""
        action = getattr(view, 'action', None)
        action_permissions = getattr(view, 'action_permissions', {})
        return action_permissions.get(action, [IsAuthenticated])
    
    def check_permission(self, permission_class, request, view):
        """检查单个权限"""
        perm = permission_class()
        
        # 检查全局权限
        if not perm.has_permission(request, view):
            self.message = getattr(perm, 'message', '权限不足')
            return False
        
        return True
    
    def has_permission(self, request, view):
        permissions_list = self.get_action_permissions(view)
        
        for perm_class in permissions_list:
            if not self.check_permission(perm_class, request, view):
                return False
        
        return True


# 便捷别名
IsAuthenticated = permissions.IsAuthenticated
AllowAny = permissions.AllowAny
