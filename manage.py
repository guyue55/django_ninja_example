#!/usr/bin/env python
"""
Django 管理脚本

这是 Django 项目的命令行管理工具，用于运行开发服务器、执行数据库迁移等管理任务。
"""

import os
import sys

if __name__ == '__main__':
    # 设置 Django 设置模块
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # 检测是否在运行测试，如果是则设置测试环境变量
    if len(sys.argv) > 1 and 'test' in sys.argv:
        os.environ['TESTING'] = 'True'
    
    try:
        # 导入 Django 管理命令执行器
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "无法导入 Django。请确认是否已安装 Django 并激活了虚拟环境。"
            "或者，您是否忘记在 Python 环境中激活虚拟环境？"
        ) from exc
    
    # 执行管理命令
    execute_from_command_line(sys.argv)