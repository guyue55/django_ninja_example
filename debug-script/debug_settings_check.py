#!/usr/bin/env python
"""检查Django设置配置"""

import os
import django
from django.conf import settings

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ['TESTING'] = 'True'

django.setup()

print("Django设置检查:")
print(f"SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
print(f"TESTING环境变量: {os.environ.get('TESTING')}")

print(f"\n实际设置值:")
print(f"TESTING: {settings.TESTING}")
print(f"DEBUG: {settings.DEBUG}")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"SECRET_KEY: {settings.SECRET_KEY[:20]}...")

# 检查是否有环境变量覆盖ALLOWED_HOSTS
allowed_hosts_env = os.environ.get('ALLOWED_HOSTS')
print(f"\nALLOWED_HOSTS环境变量: {allowed_hosts_env}")

# 检查其他相关设置
print(f"\nCSRF相关设置:")
print(f"CSRF_COOKIE_SECURE: {settings.CSRF_COOKIE_SECURE}")
print(f"CSRF_COOKIE_HTTPONLY: {settings.CSRF_COOKIE_HTTPONLY}")
print(f"CSRF_USE_SESSIONS: {settings.CSRF_USE_SESSIONS}")
print(f"CSRF_FAILURE_VIEW: {settings.CSRF_FAILURE_VIEW}")

print(f"\nCORS设置:")
print(f"CORS_ALLOWED_ORIGINS: {getattr(settings, 'CORS_ALLOWED_ORIGINS', '未设置')}")
print(f"CORS_ALLOW_ALL_ORIGINS: {getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', '未设置')}")

# 尝试手动添加testserver到ALLOWED_HOSTS
print(f"\n手动添加testserver到ALLOWED_HOSTS...")
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')
    print(f"更新后的ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
else:
    print("testserver已在ALLOWED_HOSTS中")