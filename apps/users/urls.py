"""
用户应用 URL 配置

定义用户管理相关的 URL 路由。
"""

from django.urls import path, include
from .api import router

# URL 模式 - 添加 Ninja 路由
urlpatterns = [
    path('', include(router.urls)),  # 添加 Ninja 路由到根路径
]