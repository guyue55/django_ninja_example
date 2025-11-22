#!/usr/bin/env python
"""测试JWT过期时间问题"""

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

# 测试不同的过期时间
for hours in [24, 48, 168]:  # 1天, 2天, 1周
    print(f"\n=== 测试 {hours} 小时过期时间 ===")
    
    now = datetime.utcnow()
    expire = now + timedelta(hours=hours)
    
    payload = {
        'user_id': user.id,
        'token_type': 'reset',
        'exp': int(expire.timestamp()),
        'iat': int(now.timestamp()),
        'jti': f'test_jti_{hours}',
    }
    
    print(f"当前时间 (UTC): {now}")
    print(f"过期时间 (UTC): {expire}")
    print(f"过期时间戳: {payload['exp']}")
    print(f"当前时间戳: {payload['iat']}")
    print(f"时间差 (小时): {(payload['exp'] - payload['iat']) / 3600}")
    
    # 生成令牌
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    print(f"令牌生成成功: {token[:50]}...")
    
    # 立即验证令牌
    try:
        current_timestamp = int(datetime.utcnow().timestamp())
        print(f"验证时当前时间戳: {current_timestamp}")
        print(f"令牌过期时间戳: {payload['exp']}")
        print(f"时间差 (秒): {payload['exp'] - current_timestamp}")
        
        decoded_payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={'verify_exp': True}
        )
        print(f"✓ 解码成功!")
        
    except jwt.ExpiredSignatureError as e:
        print(f"✗ 令牌已过期: {e}")
        # 获取过期详情
        decoded_without_exp = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={'verify_exp': False}
        )
        current_ts = int(datetime.utcnow().timestamp())
        print(f"  过期时间戳: {decoded_without_exp.get('exp')}")
        print(f"  当前时间戳: {current_ts}")
        print(f"  时间差: {decoded_without_exp.get('exp') - current_ts}")
        
    except Exception as e:
        print(f"✗ 其他错误: {e}")

# 检查系统时间
import subprocess
import platform
print(f"\n=== 系统时间检查 ===")
print(f"Python datetime.utcnow(): {datetime.utcnow()}")
print(f"时间戳: {int(datetime.utcnow().timestamp())}")

# 检查操作系统时间
if platform.system() == 'Windows':
    result = subprocess.run(['time', '/t'], capture_output=True, text=True)
    print(f"Windows 时间: {result.stdout.strip()}")
else:
    result = subprocess.run(['date'], capture_output=True, text=True)
    print(f"系统时间: {result.stdout.strip()}")