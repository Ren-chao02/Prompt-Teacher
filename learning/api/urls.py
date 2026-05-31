from django.urls import path
from .views import LearningMaterialViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'materials', LearningMaterialViewSet, basename='learning-material')

urlpatterns = [
    # 学习资料管理 (通过 router 自动生成 CRUD 路由)
]

urlpatterns += router.urls
