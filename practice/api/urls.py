from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'scenarios', views.PracticeScenarioViewSet)
router.register(r'topics', views.PracticeTopicViewSet)
router.register(r'records', views.PracticeRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
