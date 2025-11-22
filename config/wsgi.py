"""
WSGI 配置

WSGI 是 Web Server Gateway Interface 的缩写，是 Python Web 应用和 Web 服务器之间的标准接口。
本文件配置了 Django 应用的 WSGI 入口点。
"""

import os

from django.core.wsgi import get_wsgi_application

# 设置 Django 设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 创建 WSGI 应用实例
application = get_wsgi_application()