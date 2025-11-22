#!/usr/bin/env python
"""详细API错误调试"""

import os
import django
from django.test import Client
import json
import traceback

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'
django.setup()

client = Client(HTTP_HOST='testserver')

# 测试新用户注册 - 应该工作
print("测试新用户注册...")
new_data = {
    'username': 'debuguser',
    'email': 'debug@example.com',
    'password': 'debugpass123',
    'password_confirm': 'debugpass123',
    'nickname': '调试用户'
}

try:
    response = client.post(
        '/api/users/register',
        data=json.dumps(new_data),
        content_type='application/json'
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.content.decode()}")
    
    if response.status_code == 500:
        print(f"响应头: {dict(response.headers)}")
        
except Exception as e:
    print(f"请求异常: {e}")
    traceback.print_exc()

# 测试已存在用户 - 应该返回422
print("\n测试已存在用户...")
existing_data = {
    'username': 'testuser',  # 已存在的用户
    'email': 'different@example.com',
    'password': 'existingpass123',
    'password_confirm': 'existingpass123'
}

try:
    response = client.post(
        '/api/users/register',
        data=json.dumps(existing_data),
        content_type='application/json'
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.content.decode()}")
    
except Exception as e:
    print(f"请求异常: {e}")
    traceback.print_exc()