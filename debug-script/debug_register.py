#!/usr/bin/env python
"""调试注册错误"""

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

# 测试注册 - 详细错误信息
print("测试用户注册（详细调试）...")
registration_data = {
    'username': 'testuser123', 
    'email': 'test123@example.com', 
    'password': 'testpass123', 
    'password_confirm': 'testpass123', 
    'nickname': '测试用户'
}

try:
    response = client.post(
        '/api/users/register',
        data=json.dumps(registration_data),
        content_type='application/json'
    )
    
    print(f"注册状态码: {response.status_code}")
    print(f"注册响应: {response.content.decode()}")
    
    if response.status_code == 500:
        print("\n500错误详情:")
        print(f"响应头: {dict(response.headers)}")
        
        # 尝试获取更详细的错误信息
        try:
            error_data = json.loads(response.content)
            print(f"错误数据: {error_data}")
        except:
            print("无法解析错误响应为JSON")
            
except Exception as e:
    print(f"请求异常: {e}")
    traceback.print_exc()

# 测试简化的注册数据
print("\n测试简化注册数据...")
simple_data = {
    'username': 'simpleuser',
    'email': 'simple@example.com',
    'password': 'simplepass123',
    'password_confirm': 'simplepass123'
}

response = client.post(
    '/api/users/register',
    data=json.dumps(simple_data),
    content_type='application/json'
)

print(f"简化注册状态码: {response.status_code}")
print(f"简化注册响应: {response.content.decode()}")

# 测试已存在的用户
print("\n测试已存在用户注册...")
existing_data = {
    'username': 'testuser',  # 已存在的用户
    'email': 'existing@example.com',
    'password': 'existingpass123',
    'password_confirm': 'existingpass123'
}

response = client.post(
    '/api/users/register',
    data=json.dumps(existing_data),
    content_type='application/json'
)

print(f"已存在用户状态码: {response.status_code}")
print(f"已存在用户响应: {response.content.decode()}")