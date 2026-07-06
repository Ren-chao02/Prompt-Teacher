"""自定义认证后端 - 支持学号/工号/用户名登录"""
from django.contrib.auth.backends import ModelBackend
from .models import UserProfile


class RoleBasedAuthBackend(ModelBackend):
    """
    基于角色的认证后端。

    通过 login_type 参数决定用哪个字段查找用户：
      - 'student_id': 用 student_id 查找
      - 'employee_id': 用 employee_id 查找
      - 'username' (default): 用 username 查找
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        login_type = kwargs.get('login_type', 'username')

        if login_type == 'student_id':
            user = UserProfile.objects.filter(student_id=username).first()
        elif login_type == 'employee_id':
            user = UserProfile.objects.filter(employee_id=username).first()
        else:
            user = UserProfile.objects.filter(username=username).first()

        if not user:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
