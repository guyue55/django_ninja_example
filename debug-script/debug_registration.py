#!/usr/bin/env python
"""
调试注册API的脚本
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import json
from django.test import Client

def test_registration():
    """测试用户注册"""
    client = Client()
    
    registration_data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'newpassword123',
        'password_confirm': 'newpassword123',
        'nickname': '新用户'
    }
    
    print("发送注册请求...")
    print(f"数据: {json.dumps(registration_data, ensure_ascii=False, indent=2)}")
    
    response = client.post(
        '/api/users/register',
        data=json.dumps(registration_data),
        content_type='application/json'
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.content.decode('utf-8')}")
    
    if response.status_code == 500:
        print("\n=== 服务器错误详情 ===")
        try:
            import traceback
            # 尝试获取Django错误页面信息
            content = response.content.decode('utf-8')
            if 'Traceback' in content:
                print("找到Traceback信息:")
                print(content)
        except Exception as e:
            print(f"无法解析错误详情: {e}")

if __name__ == '__main__':
    test_registration()