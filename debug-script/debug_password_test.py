#!/usr/bin/env python
"""
调试密码更新错误的脚本 - 简化版
"""
import os
import sys
import django

# 设置 Django 环境和测试模式
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'  # 强制设置测试模式
django.setup()

import json
from django.test import Client
from apps.users.models import User

def test_password_update():
    """测试密码更新功能"""
    print(f"测试模式: {django.conf.settings.TESTING}")
    
    # 获取或创建测试用户
    try:
        user = User.objects.get(username='testuser')
        user.set_password('correctpassword')
        user.save()
        print("使用现有测试用户")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='correctpassword',
            nickname='Test User'
        )
        print("创建新测试用户")
    
    # 登录获取令牌
    client = Client()
    login_response = client.post('/api/auth/login', 
        data=json.dumps({
            'username': 'testuser',
            'password': 'correctpassword'
        }),
        content_type='application/json'
    )
    
    print(f"登录响应状态码: {login_response.status_code}")
    if login_response.status_code == 200:
        login_data = json.loads(login_response.content)
        access_token = login_data['access_token']
        print(f"获取访问令牌: {access_token[:20]}...")
        
        # 测试错误的旧密码
        print("\n测试错误的旧密码...")
        password_response = client.put('/api/users/me/password',
            data=json.dumps({
                'old_password': 'wrongoldpassword',
                'new_password': 'newsecurepassword123',
                'new_password_confirm': 'newsecurepassword123'
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        print(f"密码更新响应状态码: {password_response.status_code}")
        response_content = password_response.content.decode()
        print(f"密码更新响应内容: {response_content}")
        
        # 如果是500错误，打印更多调试信息
        if password_response.status_code == 500:
            print(f"响应头: {dict(password_response.headers)}")
            
    else:
        print(f"登录失败: {login_response.content.decode()}")

if __name__ == '__main__':
    test_password_update()