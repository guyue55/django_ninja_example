#!/usr/bin/env python
"""详细错误诊断"""

import os
import django
from django.test import Client
import json
import logging

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('django')
logger.setLevel(logging.DEBUG)

django.setup()

from django.conf import settings

print("当前设置:")
print(f"TESTING: {settings.TESTING}")
print(f"DEBUG: {settings.DEBUG}")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")

client = Client(HTTP_HOST='testserver')

# 测试简单的根路径
print("\n测试根路径...")
try:
    response = client.get('/')
    print(f"根路径状态码: {response.status_code}")
    if response.status_code == 400:
        print(f"根路径响应: {response.content.decode()}")
except Exception as e:
    print(f"根路径错误: {e}")

# 测试管理后台
print("\n测试管理后台...")
try:
    response = client.get('/admin/')
    print(f"管理后台状态码: {response.status_code}")
    if response.status_code == 400:
        print(f"管理后台响应: {response.content.decode()[:500]}")
except Exception as e:
    print(f"管理后台错误: {e}")

# 测试API根路径
print("\n测试API根路径...")
try:
    response = client.get('/api/')
    print(f"API根路径状态码: {response.status_code}")
    if response.status_code == 400:
        print(f"API根路径响应: {response.content.decode()[:500]}")
except Exception as e:
    print(f"API根路径错误: {e}")

# 测试健康检查
print("\n测试健康检查...")
try:
    response = client.get('/api/health/')
    print(f"健康检查状态码: {response.status_code}")
    if response.status_code == 400:
        print(f"健康检查响应: {response.content.decode()[:500]}")
except Exception as e:
    print(f"健康检查错误: {e}")

# 检查中间件
print(f"\n中间件配置: {settings.MIDDLEWARE}")