#!/usr/bin/env python
"""
测试运行脚本

用于在Windows环境下运行测试，避免调试工具栏干扰
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    # 设置测试环境变量
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    os.environ.setdefault('TESTING', 'true')
    os.environ.setdefault('REDIS_URL', 'memory://')  # 使用内存缓存代替Redis
    os.environ.setdefault('CACHE_BACKEND', 'django.core.cache.backends.locmem.LocMemCache')  # 使用本地内存缓存
    
    # 配置Django
    django.setup()
    
    # 获取测试运行器
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False)
    
    # 运行测试
    failures = test_runner.run_tests(['tests'])
    
    # 退出码
    sys.exit(bool(failures))