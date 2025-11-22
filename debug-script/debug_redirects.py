#!/usr/bin/env python
"""测试URL重定向问题"""

import os
import django
from django.test import Client
import json

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'
django.setup()

client = Client(HTTP_HOST='testserver')

# 测试不同的URL变体
test_urls = [
    '/api/',
    '/api',
    '/api/health',
    '/api/health/',
    '/api/users/register',
    '/api/users/register/',
    '/api/auth/login',
    '/api/auth/login/',
]

print("测试URL重定向行为:")
for url in test_urls:
    print(f"\n测试: {url}")
    response = client.get(url, follow=False)
    print(f"  状态码: {response.status_code}")
    if response.status_code in [301, 302]:
        location = response.get('Location', '无Location头')
        print(f"  重定向到: {location}")
        
        # 跟随重定向
        if location:
            follow_response = client.get(location)
            print(f"  重定向后状态码: {follow_response.status_code}")
    elif response.status_code == 200:
        print(f"  成功访问")
    elif response.status_code == 404:
        print(f"  未找到")
    else:
        print(f"  响应: {response.content.decode()[:100]}...")