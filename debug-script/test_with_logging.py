#!/usr/bin/env python
"""
启用详细错误日志的测试脚本
"""

import os
import sys
import django
import logging

# 设置详细日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'  # 确保在测试模式下运行
django.setup()

import json
from django.test import Client

def test_with_logging():
    """启用日志的测试"""
    client = Client()
    
    print("=== 测试登录端点（带日志）===")
    login_data = {
        'username': 'testuser_1234',
        'password': 'testpass123'
    }
    
    try:
        response = client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        print(f"登录状态: {response.status_code}")
        print(f"登录响应头: {dict(response.headers)}")
        print(f"登录响应: {response.content.decode('utf-8')}")
        
    except Exception as e:
        print(f"异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_with_logging()