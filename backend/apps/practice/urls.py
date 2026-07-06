from django.urls import path
from . import views

app_name = 'practice'
urlpatterns = [
    path('', views.practice_list, name='practice'),
    path('history/', views.practice_history, name='history'),
    path('record/<int:record_id>/', views.practice_record_detail, name='detail'),
    # 注意：必须放在 <str:scenario_id>/ 之前，否则 api/topics 会被当成 scenario_id 匹配
    path('api/topics/', views.api_topics, name='api_topics'),
    path('<str:scenario_id>/', views.practice_detail, name='practice_detail'),
]
