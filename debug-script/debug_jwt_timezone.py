#!/usr/bin/env python
"""调试JWT令牌时区问题"""

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

# 立即验证令牌
try:
    decoded_payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )
    print(f"解码成功: {decoded_payload}")
    print(f"用户ID: {decoded_payload.get('user_id')}")
    print(f"令牌类型: {decoded_payload.get('token_type')}")
    print(f"过期时间戳: {decoded_payload.get('exp')}")
    print(f"当前时间戳: {int(datetime.utcnow().timestamp())}")
    print(f"是否过期: {decoded_payload.get('exp', 0) < int(datetime.utcnow().timestamp())}")
except jwt.ExpiredSignatureError:
    print("令牌已过期")
except Exception as e:
    print(f"验证失败: {e}")