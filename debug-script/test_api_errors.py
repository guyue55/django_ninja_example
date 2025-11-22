#!/usr/bin/env python
"""测试API层错误处理"""

import os
import django
from django.test import Client
import json

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'
django.setup()

client = Client(HTTP_HOST='testserver')

# 测试已存在用户 - 应该返回422而不是500
print("测试已存在用户注册（应该返回422）...")
existing_data = {
    'username': 'testuser',  # 已存在的用户
    'email': 'different@example.com',
    'password': 'existingpass123',
    'password_confirm': 'existingpass123'
}

response = client.post(
    '/api/users/register',
    data=json.dumps(existing_data),
    content_type='application/json'
)

print(f"状态码: {response.status_code}")
print(f"响应: {response.content.decode()}")

# 测试已存在邮箱 - 应该返回422
print("\n测试已存在邮箱注册（应该返回422）...")
existing_email_data = {
    'username': 'differentuser',
    'email': 'test@example.com',  # 已存在的邮箱
    'password': 'existingpass123',
    'password_confirm': 'existingpass123'
}

response = client.post(
    '/api/users/register',
    data=json.dumps(existing_email_data),
    content_type='application/json'
)

print(f"状态码: {response.status_code}")
print(f"响应: {response.content.decode()}")

# 测试新用户 - 应该返回200
print("\n测试新用户注册（应该返回200）...")
new_data = {
    'username': 'apinewuser',
    'email': 'apinew@example.com',
    'password': 'newpass123',
    'password_confirm': 'newpass123',
    'nickname': 'API新用户'
}

response = client.post(
    '/api/users/register',
    data=json.dumps(new_data),
    content_type='application/json'
)

print(f"状态码: {response.status_code}")
if response.status_code == 200:
    data = json.loads(response.content)
    print(f"注册成功: {data['username']} (ID: {data['id']})")
else:
    print(f"响应: {response.content.decode()}")