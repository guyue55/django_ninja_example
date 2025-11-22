#!/usr/bin/env python
"""进一步调试JWT时区问题"""

import os
import django
from django.conf import settings
import jwt
from datetime import datetime, timedelta
import time

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'  # 强制设置为测试模式
django.setup()

from apps.users.models import User
import uuid

# 创建测试用户
user = User.objects.create_user(
    username=f'testuser_{uuid.uuid4().hex[:8]}',
    email=f'test_{uuid.uuid4().hex[:8]}@example.com',
    password='testpass123'
)

print(f"用户创建成功: {user.username} (ID: {user.id})")

# 手动创建 JWT 令牌来调试时区问题
now = datetime.utcnow()
expire = now + timedelta(hours=1)

payload = {
    'user_id': user.id,
    'token_type': 'reset',
    'exp': int(expire.timestamp()),
    'iat': int(now.timestamp()),
    'jti': 'test_jti_12345',
}

print(f"当前时间 (UTC): {now}")
print(f"过期时间 (UTC): {expire}")
print(f"过期时间戳: {payload['exp']}")
print(f"当前时间戳: {payload['iat']}")
print(f"时间差 (秒): {payload['exp'] - payload['iat']}")

# 生成令牌
token = jwt.encode(
    payload,
    settings.JWT_SECRET_KEY,
    algorithm=settings.JWT_ALGORITHM
)

print(f"令牌生成成功: {token[:50]}...")

# 检查 JWT 时间相关设置
print(f"JWT 算法: {settings.JWT_ALGORITHM}")
print(f"JWT 密钥: {settings.JWT_SECRET_KEY[:10]}...")

# 立即验证令牌 - 添加更多调试信息
try:
    # 获取当前时间戳
    current_timestamp = int(datetime.utcnow().timestamp())
    print(f"验证时当前时间戳: {current_timestamp}")
    print(f"令牌过期时间戳: {payload['exp']}")
    print(f"时间差 (过期时间 - 当前时间): {payload['exp'] - current_timestamp}")
    
    decoded_payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        options={'verify_exp': True}
    )
    print(f"解码成功: {decoded_payload}")
    
except jwt.ExpiredSignatureError as e:
    print(f"令牌已过期: {e}")
    # 尝试不解码过期验证来获取原始数据
    try:
        decoded_without_exp = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={'verify_exp': False}
        )
        print(f"不过期验证的解码数据: {decoded_without_exp}")
        print(f"过期时间戳: {decoded_without_exp.get('exp')}")
        print(f"当前时间戳: {int(datetime.utcnow().timestamp())}")
    except Exception as inner_e:
        print(f"即使不过期验证也失败: {inner_e}")
        
except Exception as e:
    print(f"其他验证失败: {e}")
    import traceback
    traceback.print_exc()