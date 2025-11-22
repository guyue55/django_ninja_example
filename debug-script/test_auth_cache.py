#!/usr/bin/env python
"""测试认证服务缓存问题"""

import os
import django
from django.conf import settings

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'  # 强制设置为测试模式
django.setup()

from apps.authentication.services import AuthService
from apps.users.models import User

# 创建测试用户（如果不存在）
try:
    user = User.objects.get(username='testuser')
    print(f"用户已存在: {user.username}")
except User.DoesNotExist:
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    print(f"用户创建成功: {user.username}")

print(f"TESTING 设置: {settings.TESTING}")
print(f"缓存配置: {settings.CACHES}")

# 测试生成令牌
try:
    token_data = AuthService.generate_tokens(user)
    print(f"令牌生成成功: {token_data.keys()}")
except Exception as e:
    print(f"令牌生成失败: {e}")
    import traceback
    traceback.print_exc()