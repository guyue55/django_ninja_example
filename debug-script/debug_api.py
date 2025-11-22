#!/usr/bin/env python
"""调试API端点"""

import os
import django
from django.test import Client
import json

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'
django.setup()

client = Client()

# 测试注册端点
print("测试注册端点...")
response = client.post('/api/users/register', 
    json.dumps({
        'username': 'testuser123', 
        'email': 'test123@example.com', 
        'password': 'testpass123', 
        'password_confirm': 'testpass123', 
        'nickname': '测试用户'
    }), 
    content_type='application/json'
)

print(f"Status code: {response.status_code}")
print(f'Response: {response.content.decode()}')
if response.status_code in [301, 302]:
    print(f'Redirect to: {response.get("Location", "No Location header")}')

# 测试带斜杠的注册端点
print("\n测试带斜杠的注册端点...")
response = client.post('/api/users/register/', 
    json.dumps({
        'username': 'testuser456', 
        'email': 'test456@example.com', 
        'password': 'testpass123', 
        'password_confirm': 'testpass123', 
        'nickname': '测试用户2'
    }), 
    content_type='application/json'
)

print(f"Status code: {response.status_code}")
print(f'Response: {response.content.decode()}')
if response.status_code in [301, 302]:
    print(f'Redirect to: {response.get("Location", "No Location header")}')