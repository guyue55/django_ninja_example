#!/usr/bin/env python
"""直接测试用户服务"""

import os
import django
import json
import traceback

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'
django.setup()

from apps.users.services import UserService
from apps.users.schemas import UserCreate
from pydantic import ValidationError

# 测试数据
test_data = {
    'username': 'testuser123', 
    'email': 'test123@example.com', 
    'password': 'testpass123', 
    'password_confirm': 'testpass123', 
    'nickname': '测试用户'
}

print("测试Pydantic模式验证...")
try:
    # 测试模式验证
    user_create = UserCreate(**test_data)
    print(f"模式验证成功: {user_create}")
    print(f"验证后的数据: {user_create.dict()}")
    
except ValidationError as e:
    print(f"模式验证失败: {e}")
    print(f"错误详情: {e.errors()}")

print("\n测试用户服务创建...")
try:
    # 测试用户服务
    user_data = test_data.copy()
    user = UserService.create_user(user_data)
    print(f"用户创建成功: {user.username} (ID: {user.id})")
    
except Exception as e:
    print(f"用户创建失败: {e}")
    print(f"错误类型: {type(e)}")
    traceback.print_exc()

# 测试已存在用户
print("\n测试已存在用户...")
try:
    user_data = test_data.copy()
    user_data['username'] = 'testuser'  # 已存在的用户
    user_data['email'] = 'different@example.com'
    user = UserService.create_user(user_data)
    print(f"用户创建成功: {user.username}")
    
except Exception as e:
    print(f"已存在用户创建失败: {e}")
    print(f"错误类型: {type(e)}")

# 测试密码验证
print("\n测试密码验证...")
try:
    from django.contrib.auth.password_validation import validate_password
    
    # 测试弱密码
    weak_password = "123"
    validate_password(weak_password)
    print("弱密码验证通过")
    
except Exception as e:
    print(f"弱密码验证失败: {e}")
    
# 测试强密码
try:
    strong_password = "testpass123"
    validate_password(strong_password)
    print("强密码验证通过")
    
except Exception as e:
    print(f"强密码验证失败: {e}")