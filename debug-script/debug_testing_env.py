#!/usr/bin/env python
"""检查测试环境设置"""

import os
import sys

# 模拟 manage.py 的行为
print(f"sys.argv: {sys.argv}")
print(f"'test' in sys.argv: {'test' in sys.argv}")

if len(sys.argv) > 1 and 'test' in sys.argv:
    os.environ['TESTING'] = 'True'
    print("设置 TESTING=True")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
from django.conf import settings

django.setup()

print(f"TESTING 环境变量: {os.environ.get('TESTING')}")
print(f"settings.TESTING: {settings.TESTING}")
print(f"settings.DEBUG: {settings.DEBUG}")

# 检查是否包含 debug_toolbar
print(f"debug_toolbar in INSTALLED_APPS: {'debug_toolbar' in settings.INSTALLED_APPS}")
print(f"debug_toolbar.middleware.DebugToolbarMiddleware in MIDDLEWARE: {'debug_toolbar.middleware.DebugToolbarMiddleware' in settings.MIDDLEWARE}")