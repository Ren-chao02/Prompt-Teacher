from django.urls import path
from . import views

app_name = 'practice'
urlpatterns = [
    path('', views.practice_view, name='practice'),
    path('history/', views.practice_history, name='history'),
    path('detail/<int:record_id>/', views.practice_detail, name='detail'),
]
