#!/usr/bin/env python
"""调试API注册错误"""

import os
import django
from django.conf import settings

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'  # 强制设置为测试模式
django.setup()

from django.test import Client
import json

# 创建测试客户端
client = Client()

# 测试用户注册
registration_data = {
    'username': 'testuser_api',
    'email': 'testapi@example.com',
    'password': 'testpass123',
    'password_confirm': 'testpass123',
    'nickname': 'API测试用户'
}

print(f"注册数据: {registration_data}")

try:
    response = client.post(
        '/api/auth/register',
        data=json.dumps(registration_data),
        content_type='application/json'
    )
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.content.decode()}")
    
    if response.status_code >= 400:
        print(f"错误详情:")
        try:
            error_data = json.loads(response.content)
            print(f"  错误数据: {error_data}")
        except:
            print(f"  原始响应: {response.content.decode()}")
            
except Exception as e:
    print(f"请求失败: {e}")
    import traceback
    traceback.print_exc()