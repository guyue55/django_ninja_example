#!/usr/bin/env python
"""测试用户服务错误处理"""

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
from django.core.exceptions import ValidationError

# 测试数据
test_data = {
    'username': 'newtestuser', 
    'email': 'newtest@example.com', 
    'password': 'testpass123', 
    'password_confirm': 'testpass123', 
    'nickname': '新测试用户'
}

print("测试用户服务创建（新用户）...")
try:
    # 测试用户服务
    user_data = test_data.copy()
    user = UserService.create_user(user_data)
    print(f"用户创建成功: {user.username} (ID: {user.id})")
    
except ValidationError as e:
    print(f"验证错误: {e}")
    print(f"错误详情: {e.messages}")
except Exception as e:
    print(f"其他错误: {e}")
    print(f"错误类型: {type(e)}")
    traceback.print_exc()

# 测试已存在的用户
print("\n测试已存在用户...")
try:
    user_data = test_data.copy()
    user_data['username'] = 'testuser'  # 已存在的用户
    user_data['email'] = 'different@example.com'
    user = UserService.create_user(user_data)
    print(f"用户创建成功: {user.username}")
    
except ValidationError as e:
    print(f"验证错误: {e}")
    print(f"错误详情: {e.messages}")
except Exception as e:
    print(f"其他错误: {e}")
    print(f"错误类型: {type(e)}")

# 测试已存在的邮箱
print("\n测试已存在邮箱...")
try:
    user_data = test_data.copy()
    user_data['username'] = 'differentuser'
    user_data['email'] = 'test@example.com'  # 已存在的邮箱
    user = UserService.create_user(user_data)
    print(f"用户创建成功: {user.username}")
    
except ValidationError as e:
    print(f"验证错误: {e}")
    print(f"错误详情: {e.messages}")
except Exception as e:
    print(f"其他错误: {e}")
    print(f"错误类型: {type(e)}")