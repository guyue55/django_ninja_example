#!/usr/bin/env python
"""
测试API路由的脚本
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

def test_api_routes():
    """测试API路由"""
    client = Client()
    
    # 测试基本API端点
    print("=== 测试API根路径 ===")
    response = client.get('/api/')
    print(f"API根路径状态: {response.status_code}")
    if response.status_code == 200:
        print(f"API信息: {response.content.decode('utf-8')}")
    
    print("\n=== 测试API文档 ===")
    response = client.get('/api/docs/')
    print(f"API文档状态: {response.status_code}")
    
    print("\n=== 测试用户注册端点 ===")
    response = client.get('/api/users/register')
    print(f"注册端点GET状态: {response.status_code}")
    
    print("\n=== 测试认证端点 ===")
    response = client.get('/api/auth/login')
    print(f"登录端点GET状态: {response.status_code}")

if __name__ == '__main__':
    test_api_routes()