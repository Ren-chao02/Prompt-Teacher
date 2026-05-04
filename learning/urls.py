from django.urls import path
from . import views

app_name = 'learning'
urlpatterns = [
    path('', views.learning_list, name='list'),
    path('<int:material_id>/', views.learning_detail, name='detail'),
]
