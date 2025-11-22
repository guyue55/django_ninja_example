#!/usr/bin/env python
"""
测试无认证的API请求
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'  # 确保在测试模式下运行
django.setup()

import json
from django.test import Client

def test_no_auth_api():
    """测试无认证的API请求"""
    client = Client()
    
    # 测试登录端点（应该不需要认证）
    print("=== 测试登录端点 ===")
    login_data = {
        'username': 'testuser_1234',
        'password': 'testpass123'
    }
    
    response = client.post(
        '/api/auth/login',
        data=json.dumps(login_data),
        content_type='application/json'
    )
    
    print(f"登录状态: {response.status_code}")
    print(f"登录响应: {response.content.decode('utf-8')}")
    
    # 测试注册端点（应该不需要认证）
    print("\n=== 测试注册端点 ===")
    registration_data = {
        'username': 'newuser_5678',
        'email': 'newuser_5678@example.com',
        'password': 'newpassword123',
        'password_confirm': 'newpassword123',
        'nickname': '新用户'
    }
    
    response = client.post(
        '/api/users/register',
        data=json.dumps(registration_data),
        content_type='application/json'
    )
    
    print(f"注册状态: {response.status_code}")
    print(f"注册响应: {response.content.decode('utf-8')}")

if __name__ == '__main__':
    test_no_auth_api()