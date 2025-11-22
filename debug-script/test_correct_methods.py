#!/usr/bin/env python
"""测试正确的HTTP方法和URL"""

import os
import django
from django.test import Client
import json

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'
django.setup()

client = Client(HTTP_HOST='testserver')

# 测试注册 - 使用正确的POST方法
print("测试用户注册（POST）...")
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
    content_type='application/json'
)

print(f"注册状态码: {response.status_code}")
if response.status_code == 200:
    data = json.loads(response.content)
    print(f"注册成功: {data}")
elif response.status_code in [400, 422]:
    print(f"验证错误: {response.content.decode()}")
else:
    print(f"注册响应: {response.content.decode()}")

# 测试登录 - 使用正确的POST方法
print("\n测试用户登录（POST）...")
login_data = {
    'username': 'testuser',
    'password': 'testpass123'
}

response = client.post(
    '/api/auth/login',
    data=json.dumps(login_data),
    content_type='application/json'
)

print(f"登录状态码: {response.status_code}")
if response.status_code == 200:
    data = json.loads(response.content)
    print(f"登录成功，令牌: {data.get('access_token', '无令牌')[:20]}...")
elif response.status_code == 401:
    print(f"认证失败: {response.content.decode()}")
else:
    print(f"登录响应: {response.content.decode()}")

# 测试健康检查 - 使用GET方法
print("\n测试健康检查（GET）...")
response = client.get('/api/health/')
print(f"健康检查状态码: {response.status_code}")
if response.status_code == 200:
    data = json.loads(response.content)
    print(f"健康状态: {data}")
else:
    print(f"健康检查响应: {response.content.decode()}")