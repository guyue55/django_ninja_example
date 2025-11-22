#!/usr/bin/env python
"""测试认证服务中的JWT过期时间问题"""

import os
import django
from django.conf import settings
from datetime import timedelta

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'  # 强制设置为测试模式
django.setup()

from apps.authentication.services import AuthService
from apps.users.models import User
import uuid

# 创建测试用户
user = User.objects.create_user(
    username=f'testuser_{uuid.uuid4().hex[:8]}',
    email=f'test_{uuid.uuid4().hex[:8]}@example.com',
    password='testpass123'
)

print(f"用户创建成功: {user.username} (ID: {user.id})")

# 测试认证服务中的令牌生成
print("\n=== 测试认证服务生成密码重置令牌 ===")
try:
    reset_token = AuthService.generate_password_reset_token(user)
    print(f"重置令牌生成成功: {reset_token[:50]}...")
    
    # 立即验证
    verified_user = AuthService.verify_password_reset_token(reset_token)
    print(f"验证结果: {verified_user}")
    
    if verified_user is None:
        print("验证失败，检查日志...")
        
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()

# 检查认证服务中的过期时间设置
print(f"\n=== 认证服务配置 ===")
print(f"JWT 过期小时数: {settings.JWT_EXPIRATION_HOURS}")
print(f"JWT 刷新过期天数: {settings.JWT_REFRESH_EXPIRATION_DAYS}")

# 手动测试不同的小时过期时间
print(f"\n=== 测试不同过期时间 ===")
for hours in [1, 2, 6, 12, 24]:
    print(f"\n测试 {hours} 小时过期时间:")
    try:
        # 使用内部方法生成令牌
        token = AuthService._generate_token(
            user_id=user.id,
            token_type='reset',
            expires_delta=timedelta(hours=hours)
        )
        print(f"  令牌生成成功: {token[:30]}...")
        
        # 验证令牌
        verified_user = AuthService.verify_password_reset_token(token)
        print(f"  验证结果: {'成功' if verified_user else '失败'}")
        
    except Exception as e:
        print(f"  测试失败: {e}")