from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from core.views import home_view, admin_spa_view
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # Django原生后台管理（移到 /django-admin/）
    path('django-admin/', admin.site.urls),
    
    # Vue管理后台SPA（接管 /admin/ 路径）
    # 必须放在API路由之前，避免冲突
    re_path(r'^admin/(?P<path>.*)$', admin_spa_view, name='admin-spa'),
    
    # 前台页面
    path('', home_view, name='home'),
    path('users/', include('users.urls')),
    path('practice/', include('practice.urls')),
    path('learning/', include('learning.urls')),
    
    # REST API (v1)
    path('api/v1/', include('users.api.urls')),
    path('api/v1/learning/', include('learning.api.urls')),
    path('api/v1/practice/', include('practice.api.urls')),
    path('api/v1/analytics/', include('analytics.api.urls')),
    path('api/v1/notifications/', include('notifications.api.urls')),
    
    # API 文档 (Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)