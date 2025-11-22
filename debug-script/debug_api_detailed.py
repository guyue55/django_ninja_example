#!/usr/bin/env python
"""详细调试API端点"""

import os
import django
from django.test import Client
import json

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'
django.setup()

client = Client()

# 测试注册端点 - 详细版本
print("测试注册端点 - 详细版本...")
registration_data = {
    'username': 'testuser123', 
    'email': 'test123@example.com', 
    'password': 'testpass123', 
    'password_confirm': 'testpass123', 
    'nickname': '测试用户'
}

response = client.post(
    '/api/users/register', 
    data=json.dumps(registration_data),
    content_type='application/json',
    follow=True  # 跟随重定向
)

print(f"Status code: {response.status_code}")
print(f"Response: {response.content.decode()}")
print(f"Headers: {dict(response.headers)}")

# 测试登录端点
print("\n测试登录端点...")
login_data = {
    'username': 'testuser',
    'password': 'testpass123'
}

response = client.post(
    '/api/auth/login',
    data=json.dumps(login_data),
    content_type='application/json',
    follow=True
)

print(f"Status code: {response.status_code}")
print(f"Response: {response.content.decode()[:200]}...")

# 测试带授权头的用户信息获取
print("\n测试获取用户信息...")
# 首先登录获取令牌
response = client.post(
    '/api/auth/login',
    data=json.dumps({'username': 'testuser', 'password': 'testpass123'}),
    content_type='application/json'
)

if response.status_code == 200:
    data = json.loads(response.content)
    if 'access_token' in data:
        token = data['access_token']
        print(f"获取到令牌: {token[:20]}...")
        
        # 使用令牌获取用户信息
        response = client.get(
            '/api/users/me',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        print(f"用户信息获取状态码: {response.status_code}")
        print(f"用户信息响应: {response.content.decode()[:200]}...")
    else:
        print(f"登录响应中没有令牌: {data}")
else:
    print(f"登录失败: {response.status_code}")
    print(f"登录响应: {response.content.decode()}")