#!/usr/bin/env python
"""调试测试环境中的缓存问题"""

import os
import sys

# 在导入 Django 之前设置测试环境
os.environ['TESTING'] = 'True'
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

import django
django.setup()

from django.conf import settings
from django.core.cache import cache

print(f"Python 版本: {sys.version}")
print(f"Django 版本: {django.VERSION}")
print(f"TESTING 环境变量: {os.environ.get('TESTING')}")
print(f"TESTING 设置: {settings.TESTING}")
print(f"DEBUG 设置: {settings.DEBUG}")
print(f"缓存配置: {settings.CACHES}")
print(f"缓存后端类型: {type(cache)}")
print(f"缓存后端模块: {cache.__class__.__module__}")

# 检查缓存后端的实际类型
from django.core.cache.backends.locmem import LocMemCache
if hasattr(cache, '_cache'):
    print(f"缓存后端实例: {type(cache._cache)}")
    print(f"是 LocMemCache 吗: {isinstance(cache._cache, LocMemCache)}")

# 测试缓存操作
try:
    cache.set('test_key', 'test_value', 60)
    value = cache.get('test_key')
    print(f"缓存测试成功: {value}")
except Exception as e:
    print(f"缓存测试失败: {e}")
    import traceback
    traceback.print_exc()

# 检查是否有 Redis 相关的导入
import sys
redis_modules = [name for name in sys.modules.keys() if 'redis' in name]
print(f"已导入的 Redis 模块: {redis_modules}")

# 检查 Django 缓存配置
from django.core.cache import caches
print(f"所有缓存配置: {caches.settings}")

# 尝试获取默认缓存的配置
default_cache = caches['default']
print(f"默认缓存实例: {type(default_cache)}")
if hasattr(default_cache, '_cache'):
    print(f"默认缓存后端: {type(default_cache._cache)}")