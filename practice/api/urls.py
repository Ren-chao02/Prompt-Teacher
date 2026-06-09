from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'scenarios', views.PracticeScenarioViewSet)
router.register(r'topics', views.PracticeTopicViewSet)
router.register(r'records', views.PracticeRecordViewSet)
router.register(r'llm-configs', views.LLMConfigViewSet, basename='llm-config')

urlpatterns = [
    path('', include(router.urls)),
]
