#!/usr/bin/env python
"""
测试认证Bearer的脚本
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'  # 确保在测试模式下运行
django.setup()

from apps.api.api import AuthBearer
from django.test import RequestFactory

class MockRequest:
    """模拟请求对象"""
    def __init__(self):
        self.META = {}
        self.user_id = None

def test_auth_bearer():
    """测试认证Bearer"""
    print("=== 测试AuthBearer ===")
    
    auth_bearer = AuthBearer()
    
    # 测试无token的情况
    request = MockRequest()
    result = auth_bearer.authenticate(request, "")
    print(f"空token验证结果: {result}")
    
    # 测试无效token
    result = auth_bearer.authenticate(request, "invalid_token")
    print(f"无效token验证结果: {result}")
    
    # 测试有效token（需要先生成一个）
    from apps.authentication.services import AuthService
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # 创建测试用户
    try:
        import random
        username = f'testuser_{random.randint(1000, 9999)}'
        email = f'test_{random.randint(1000, 9999)}@example.com'
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password='testpass123'
        )
        
        # 生成token
        token_data = AuthService.generate_tokens(user)
        access_token = token_data['access_token']
        
        print(f"生成的token: {access_token[:20]}...")
        
        # 测试有效token
        result = auth_bearer.authenticate(request, access_token)
        print(f"有效token验证结果: {result}")
        
        # 清理
        user.delete()
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_auth_bearer()