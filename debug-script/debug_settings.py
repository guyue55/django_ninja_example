#!/usr/bin/env python
"""检查设置和CSRF配置"""

import os
import django
from django.test import Client
import json

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'
django.setup()

from django.conf import settings

print("当前设置:")
print(f"TESTING: {settings.TESTING}")
print(f"DEBUG: {settings.DEBUG}")
print(f"CSRF保护: {settings.CSRF_COOKIE_SECURE}")

# 检查Ninja API的CSRF配置
from apps.api.api import api
print(f"API CSRF配置: {api.csrf}")

client = Client()

# 测试简单的GET请求
print("\n测试GET请求...")
response = client.get('/api/users/register')
print(f"GET状态码: {response.status_code}")
print(f"GET响应: {response.content.decode()[:200]}")

# 测试POST请求不带数据
print("\n测试POST请求（空数据）...")
response = client.post('/api/users/register')
print(f"POST状态码: {response.status_code}")
print(f"POST响应: {response.content.decode()[:200]}")

# 测试POST请求带数据
print("\n测试POST请求（JSON数据）...")
response = client.post(
    '/api/users/register',
    data=json.dumps({'test': 'data'}),
    content_type='application/json'
)
print(f"POST JSON状态码: {response.status_code}")
print(f"POST JSON响应: {response.content.decode()[:200]}")

# 测试健康检查端点（应该总是可访问）
print("\n测试健康检查端点...")
response = client.get('/api/health/')
print(f"健康检查状态码: {response.status_code}")
print(f"健康检查响应: {response.content.decode()[:200]}")