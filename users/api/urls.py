from django.urls import path
from .views import (
    LoginAPIView,
    LogoutAPIView,
    CurrentUserAPIView,
    ChangePasswordAPIView,
    UserViewSet,
)
from rest_framework.routers import DefaultRouter

# 创建路由器
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # 认证相关
    path('auth/login/', LoginAPIView.as_view(), name='login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='logout'),
    path('auth/me/', CurrentUserAPIView.as_view(), name='current-user'),
    path('auth/password/change/', ChangePasswordAPIView.as_view(), name='change-password'),
    
    # 用户管理 (通过 router 自动生成 CRUD 路由)
]

# 添加路由器的 URL
urlpatterns += router.urls
