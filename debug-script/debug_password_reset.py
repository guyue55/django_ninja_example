#!/usr/bin/env python
"""调试密码重置令牌问题"""

import os
import django
from django.conf import settings

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'  # 强制设置为测试模式
django.setup()

from apps.authentication.services import AuthService
from apps.users.models import User

# 创建测试用户
import uuid
user = User.objects.create_user(
    username=f'testuser_{uuid.uuid4().hex[:8]}',
    email=f'test_{uuid.uuid4().hex[:8]}@example.com',
    password='testpass123'
)

print(f"用户创建成功: {user.username} (ID: {user.id})")

# 生成密码重置令牌
try:
    reset_token = AuthService.generate_password_reset_token(user)
    print(f"重置令牌生成成功: {reset_token[:50]}...")
    
    # 验证重置令牌
    verified_user = AuthService.verify_password_reset_token(reset_token)
    print(f"验证用户: {verified_user}")
    print(f"原始用户: {user}")
    print(f"用户ID匹配: {verified_user.id if verified_user else 'None'} == {user.id}")
    
    # 检查用户状态
    print(f"用户是否被删除: {user.is_deleted}")
    print(f"用户是否活跃: {user.is_active}")
    
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()