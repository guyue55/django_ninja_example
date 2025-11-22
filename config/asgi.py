"""
ASGI 配置

ASGI 是 Asynchronous Server Gateway Interface 的缩写，是 WSGI 的异步继任者。
本文件配置了 Django 应用的 ASGI 入口点，支持 WebSocket 等异步功能。
"""

import os

from django.core.asgi import get_asgi_application

# 设置 Django 设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 创建 ASGI 应用实例
application = get_asgi_application()