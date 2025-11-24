"""
Django 项目主 URL 配置

本文件定义了项目的所有 URL 路由，包括管理后台、API 接口等。
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# 导入 Ninja API 实例
from apps.api.api import api

urlpatterns = [
    # Django 管理后台
    path('admin/', admin.site.urls),
    
    # Web界面页面
    path('', include(('apps.web.urls', 'web'), namespace='web')),
    
    # Ninja API 接口
    path('api/', api.urls),
]

# 开发环境下的静态文件和媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # 调试工具栏（仅在非测试环境下启用）
    if not settings.TESTING:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns