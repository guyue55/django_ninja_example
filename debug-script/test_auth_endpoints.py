#!/usr/bin/env python
"""测试认证API端点"""

import os
import django
from django.test import Client
import json

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'
django.setup()

client = Client(HTTP_HOST='testserver')

# 测试登录
print("测试用户登录...")
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
    token = data.get('access_token')
    print(f"获取到令牌: {token[:20]}...")
else:
    print(f"登录失败: {response.content.decode()}")
    exit(1)

# 测试获取用户信息 - 使用认证头
print("\n测试获取用户信息（带认证）...")
response = client.get(
    '/api/users/me',
    HTTP_AUTHORIZATION=f'Bearer {token}'
)

print(f"用户信息状态码: {response.status_code}")
if response.status_code == 200:
    data = json.loads(response.content)
    print(f"用户信息: {data}")
elif response.status_code == 401:
    print(f"认证失败: {response.content.decode()}")
else:
    print(f"其他错误: {response.content.decode()}")

# 测试获取用户信息 - 不带认证
print("\n测试获取用户信息（无认证）...")
response = client.get('/api/users/me')
print(f"无认证状态码: {response.status_code}")
print(f"无认证响应: {response.content.decode()}")

# 测试更新用户信息
print("\n测试更新用户信息...")
update_data = {
    'nickname': '新昵称',
    'email': 'newemail@example.com'
}

response = client.put(
    '/api/users/me',
    data=json.dumps(update_data),
    content_type='application/json',
    HTTP_AUTHORIZATION=f'Bearer {token}'
)

print(f"更新状态码: {response.status_code}")
if response.status_code == 200:
    data = json.loads(response.content)
    print(f"更新成功: {data}")
else:
    print(f"更新失败: {response.content.decode()}")