from django.urls import path
from . import views
from . import api_views

app_name = 'practice'
urlpatterns = [
    path('', views.practice_list, name='practice'),
    path('history/', views.practice_history, name='history'),
    path('record/<int:record_id>/', views.practice_record_detail, name='detail'),
    path('<str:scenario_id>/', views.practice_detail, name='practice_detail'),
    path('api/topics/', api_views.api_get_topics, name='api_topics'),
]
