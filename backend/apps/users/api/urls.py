from django.urls import path
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
from rest_framework.routers import DefaultRouter

# 创建路由器
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'classes', ClassInfoViewSet, basename='classinfo')

urlpatterns = [
    # 认证相关
    path('auth/login/', LoginAPIView.as_view(), name='login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='logout'),
    path('auth/me/', CurrentUserAPIView.as_view(), name='current-user'),
    path('auth/password/change/', ChangePasswordAPIView.as_view(), name='change-password'),
    path('auth/my_classes/', MyClassesAPIView.as_view(), name='my-classes'),
    path('teacher/workspace/', TeacherWorkspaceView.as_view(), name='teacher-workspace'),
    path('teacher/student/<int:pk>/', TeacherStudentDetailView.as_view(), name='teacher-student-detail'),
    path('users/avatar/', CurrentUserAPIView.as_view(), name='avatar-upload'),

    # 用户管理 (通过 router 自动生成 CRUD 路由)
]

# 添加路由器的 URL
urlpatterns += router.urls
