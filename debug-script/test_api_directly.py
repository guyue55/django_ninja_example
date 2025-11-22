#!/usr/bin/env python
"""
最小化测试，直接测试API路由
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'  # 确保在测试模式下运行
django.setup()

from django.urls import path, include
from django.test import RequestFactory
from apps.api.api import api

def test_api_directly():
    """直接测试API路由"""
    print("=== 直接测试API路由 ===")
    
    # 创建请求工厂
    factory = RequestFactory()
    
    # 测试登录端点
    print("测试登录端点...")
    try:
        request = factory.post('/api/auth/login', 
                              data='{"username": "test", "password": "test"}',
                              content_type='application/json')
        
        # 获取登录视图函数
        login_view = None
        for pattern in api.urls.urlpatterns:
            if pattern.pattern._route == 'auth/login':
                login_view = pattern.callback
                break
        
        if login_view:
            response = login_view(request)
            print(f"登录响应状态: {getattr(response, 'status_code', '未知')}")
        else:
            print("找不到登录视图函数")
            
    except Exception as e:
        print(f"登录测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 列出所有可用的路由
    print("\n=== 可用路由 ===")
    try:
        for pattern in api.urls.urlpatterns:
            print(f"路由: {pattern.pattern._route}")
    except Exception as e:
        print(f"获取路由失败: {e}")

if __name__ == '__main__':
    test_api_directly()