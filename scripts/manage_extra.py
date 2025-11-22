#!/usr/bin/env python
"""
增强的 Django 管理脚本

提供额外的管理命令，用于代码格式化、检查、测试等开发任务。
"""

import os
import sys
import subprocess
from pathlib import Path

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def run_command(command, description):
    """运行系统命令"""
    print(f"\n🚀 {description}")
    print(f"命令: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"❌ 命令执行失败: {command}")
        return False
    print(f"✅ {description} 完成")
    return True

def format_code():
    """格式化代码"""
    print("\n🎨 开始代码格式化...")
    
    # Black 格式化
    if not run_command("black apps config utils --line-length=88", "Black 代码格式化"):
        return False
    
    # isort 导入排序
    if not run_command("isort apps config utils", "isort 导入排序"):
        return False
    
    print("✅ 代码格式化完成")
    return True

def lint_code():
    """代码检查"""
    print("\n🔍 开始代码检查...")
    
    # Flake8 检查
    if not run_command("flake8 apps config utils --max-line-length=88 --extend-ignore=E203,W503", "Flake8 代码检查"):
        return False
    
    # MyPy 类型检查
    if not run_command("mypy apps config utils --ignore-missing-imports", "MyPy 类型检查"):
        return False
    
    print("✅ 代码检查完成")
    return True

def run_tests():
    """运行测试"""
    print("\n🧪 开始运行测试...")
    
    if not run_command("pytest -v --cov=apps --cov-report=term-missing", "运行测试"):
        return False
    
    print("✅ 测试运行完成")
    return True

def migrate_database():
    """数据库迁移"""
    print("\n🗄️ 开始数据库迁移...")
    
    if not run_command("python manage.py makemigrations", "生成迁移文件"):
        return False
    
    if not run_command("python manage.py migrate", "执行数据库迁移"):
        return False
    
    print("✅ 数据库迁移完成")
    return True

def collect_static():
    """收集静态文件"""
    print("\n📦 开始收集静态文件...")
    
    if not run_command("python manage.py collectstatic --noinput", "收集静态文件"):
        return False
    
    print("✅ 静态文件收集完成")
    return true

def create_superuser():
    """创建超级用户"""
    print("\n👤 创建超级用户...")
    
    if not run_command("python manage.py createsuperuser", "创建超级用户"):
        return False
    
    return True

def run_dev_server():
    """运行开发服务器"""
    print("\n🚀 启动开发服务器...")
    print("访问地址: http://localhost:8000")
    print("API 文档: http://localhost:8000/api/docs/")
    print("管理后台: http://localhost:8000/admin/")
    
    run_command("python manage.py runserver", "开发服务器")

def show_help():
    """显示帮助信息"""
    print("""
增强的 Django 管理脚本

使用方法: python manage_extra.py [命令]

可用命令:
    format      - 格式化代码 (Black + isort)
    lint        - 代码检查 (Flake8 + MyPy)
    test        - 运行测试
    migrate     - 数据库迁移
    static      - 收集静态文件
    superuser   - 创建超级用户
    runserver   - 运行开发服务器
    all         - 执行所有检查 (format + lint + test + migrate + static)
    help        - 显示帮助信息

示例:
    python manage_extra.py format     # 格式化代码
    python manage_extra.py all        # 执行完整检查流程
    python manage_extra.py runserver  # 启动开发服务器
""")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1]
    
    if command == "format":
        format_code()
    elif command == "lint":
        lint_code()
    elif command == "test":
        run_tests()
    elif command == "migrate":
        migrate_database()
    elif command == "static":
        collect_static()
    elif command == "superuser":
        create_superuser()
    elif command == "runserver":
        run_dev_server()
    elif command == "all":
        print("🔧 执行完整检查流程...")
        success = True
        success &= format_code()
        success &= lint_code()
        success &= run_tests()
        success &= migrate_database()
        success &= collect_static()
        
        if success:
            print("\n✅ 所有检查通过！项目状态良好。")
        else:
            print("\n❌ 某些检查失败，请查看输出信息。")
            sys.exit(1)
    elif command == "help":
        show_help()
    else:
        print(f"❌ 未知命令: {command}")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()