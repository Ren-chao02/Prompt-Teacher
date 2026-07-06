import os
import mimetypes
from django.http import HttpResponse, Http404
from django.conf import settings
from django.shortcuts import render


def home_view(request):
    return render(request, 'home.html')


def admin_spa_view(request, path=''):
    """
    服务Vue管理后台SPA（单页应用）。
    
    对于静态资源（JS/CSS/图片等），直接返回文件内容。
    对于路由路径（如 /admin/login, /admin/dashboard），返回 index.html，
    由Vue Router在客户端处理实际路由。
    """
    dist_dir = os.path.join(settings.BASE_DIR, 'admin-panel', 'dist')
    index_path = os.path.join(dist_dir, 'index.html')
    
    # 如果存在具体路径，尝试作为静态资源返回
    if path:
        file_path = os.path.normpath(os.path.join(dist_dir, path))
        # 安全检查：确保文件在dist目录内
        if not file_path.startswith(os.path.normpath(dist_dir)):
            raise Http404('Invalid path')
        
        if os.path.isfile(file_path):
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = 'application/octet-stream'
            
            with open(file_path, 'rb') as f:
                return HttpResponse(f.read(), content_type=content_type)
    
    # SPA路由：返回 index.html
    if os.path.isfile(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            html = f.read()
        response = HttpResponse(html, content_type='text/html; charset=utf-8')
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
        response['Pragma'] = 'no-cache'
        return response
    
    # 如果 index.html 不存在，提示构建
    return HttpResponse(
        '<h1>管理后台尚未构建</h1>'
        '<p>请先执行以下命令构建前端：</p>'
        '<pre>cd admin-panel && npm run build</pre>'
        '<hr>'
        '<p><a href="/">返回首页</a></p>',
        content_type='text/html; charset=utf-8'
    )