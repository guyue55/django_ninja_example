#!/usr/bin/env python
"""测试缓存配置"""

import os
import django
from django.conf import settings

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'  # 强制设置为测试模式
django.setup()

from django.core.cache import cache

print(f"TESTING 设置: {settings.TESTING}")
print(f"DEBUG 设置: {settings.DEBUG}")
print(f"缓存配置: {settings.CACHES}")
print(f"缓存后端类型: {type(cache)}")
print(f"缓存后端模块: {cache.__class__.__module__}")

# 测试缓存操作
try:
    cache.set('test_key', 'test_value', 60)
    value = cache.get('test_key')
    print(f"缓存测试成功: {value}")
except Exception as e:
    print(f"缓存测试失败: {e}")