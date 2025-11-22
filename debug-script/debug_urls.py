#!/usr/bin/env python
"""检查URL配置"""

import os
import django
from django.test import Client
import json

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'
django.setup()

# 检查URL配置
from django.urls import reverse, resolve
from apps.api.api import api

print("检查API URLs...")
print("API URLs:")
for url_pattern in api.urls[0]:
    print(f"  Pattern: {url_pattern.pattern}, Name: {url_pattern.name}")

print("\n测试基础URL...")
client = Client()

# 测试基础API端点
response = client.get('/api/')
print(f"API根路径状态码: {response.status_code}")

# 测试docs
response = client.get('/api/docs/')
print(f"API文档状态码: {response.status_code}")

# 测试不存在的路径
response = client.get('/api/test123')
print(f"不存在的路径状态码: {response.status_code}")

# 尝试解析URL
print("\n尝试解析URLs...")
try:
    match = resolve('/api/users/register')
    print(f"Resolved: {match}")
except Exception as e:
    print(f"无法解析 /api/users/register: {e}")

try:
    match = resolve('/api/auth/login')
    print(f"Resolved: {match}")
except Exception as e:
    print(f"无法解析 /api/auth/login: {e}")