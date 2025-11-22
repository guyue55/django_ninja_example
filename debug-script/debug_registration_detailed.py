#!/usr/bin/env python
"""
详细调试注册API的脚本
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'  # 确保在测试模式下运行
django.setup()

import json
import traceback
from django.test import Client
from apps.users.schemas import UserCreate

def test_registration_detailed():
    """详细测试用户注册"""
    client = Client()
    
    registration_data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpassword123',
        'password_confirm': 'newpassword123',
        'nickname': '新用户'
    }
    
    print("=== 测试数据验证 ===")
    try:
        # 验证数据模式
        user_data = UserCreate(**registration_data)
        print(f"数据验证成功: {user_data.dict()}")
    except Exception as e:
        print(f"数据验证失败: {e}")
        return
    
    print("\n=== 发送注册请求 ===")
    try:
        # 首先获取CSRF token
        print("获取CSRF token...")
        csrf_response = client.get('/api/users/register')
        print(f"CSRF响应状态: {csrf_response.status_code}")
        
        # 尝试不带CSRF token的请求
        response = client.post(
            '/api/users/register',
            data=json.dumps(registration_data),
            content_type='application/json'
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.content.decode('utf-8')}")
            
    except Exception as e:
        print(f"请求失败: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    test_registration_detailed()