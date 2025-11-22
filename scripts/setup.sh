#!/bin/bash

# Django 项目初始化脚本
# 用于快速设置开发环境

set -e

echo "🚀 Django-Ninja 项目初始化开始..."

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python 版本
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}❌ Python 未安装，请先安装 Python 3.8+${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python 版本: $PYTHON_VERSION${NC}"
}

# 检查 pip
check_pip() {
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
    else
        echo -e "${RED}❌ pip 未安装，请先安装 pip${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ pip 已安装${NC}"
}

# 创建虚拟环境
create_venv() {
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}📦 创建虚拟环境...${NC}"
        $PYTHON_CMD -m venv venv
        echo -e "${GREEN}✅ 虚拟环境创建完成${NC}"
    else
        echo -e "${YELLOW}📦 虚拟环境已存在，跳过创建${NC}"
    fi
}

# 激活虚拟环境
activate_venv() {
    echo -e "${YELLOW}🔧 激活虚拟环境...${NC}"
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        source venv/Scripts/activate
    else
        # Linux/Mac
        source venv/bin/activate
    fi
    echo -e "${GREEN}✅ 虚拟环境已激活${NC}"
}

# 安装依赖
install_dependencies() {
    echo -e "${YELLOW}📚 安装项目依赖...${NC}"
    $PIP_CMD install --upgrade pip setuptools wheel
    $PIP_CMD install -r requirements.txt
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
}

# 创建环境变量文件
setup_env() {
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚙️  创建环境变量文件...${NC}"
        cp .env.development .env
        echo -e "${GREEN}✅ 环境变量文件创建完成${NC}"
        echo -e "${YELLOW}⚠️  请编辑 .env 文件，修改必要的配置${NC}"
    else
        echo -e "${YELLOW}⚙️  环境变量文件已存在，跳过创建${NC}"
    fi
}

# 创建必要目录
create_directories() {
    echo -e "${YELLOW}📁 创建必要目录...${NC}"
    mkdir -p logs media staticfiles
    echo -e "${GREEN}✅ 目录创建完成${NC}"
}

# 数据库迁移
migrate_database() {
    echo -e "${YELLOW}🗄️  执行数据库迁移...${NC}"
    python manage.py makemigrations
    python manage.py migrate
    echo -e "${GREEN}✅ 数据库迁移完成${NC}"
}

# 收集静态文件
collect_static() {
    echo -e "${YELLOW}📦 收集静态文件...${NC}"
    python manage.py collectstatic --noinput
    echo -e "${GREEN}✅ 静态文件收集完成${NC}"
}

# 创建超级用户
create_superuser() {
    echo -e "${YELLOW}👤 创建超级用户...${NC}"
    echo -e "${YELLOW}请输入管理员信息:${NC}"
    python manage.py createsuperuser
    echo -e "${GREEN}✅ 超级用户创建完成${NC}"
}

# 运行测试
run_tests() {
    echo -e "${YELLOW}🧪 运行测试...${NC}"
    if command -v pytest &> /dev/null; then
        pytest -v
        echo -e "${GREEN}✅ 测试运行完成${NC}"
    else
        echo -e "${YELLOW}⚠️  pytest 未安装，跳过测试${NC}"
    fi
}

# 启动开发服务器
start_dev_server() {
    echo -e "${YELLOW}🚀 启动开发服务器...${NC}"
    echo -e "${GREEN}✅ 项目初始化完成！${NC}"
    echo -e "${YELLOW}📖 访问 API 文档: http://localhost:8000/api/docs/${NC}"
    echo -e "${YELLOW}🔧 访问管理后台: http://localhost:8000/admin/${NC}"
    echo -e "${YELLOW}📊 访问健康检查: http://localhost:8000/api/health/${NC}"
    echo -e "${YELLOW}🔄 按 Ctrl+C 停止服务器${NC}"
    python manage.py runserver
}

# 主函数
main() {
    echo -e "${GREEN}🎯 Django-Ninja 项目初始化脚本${NC}"
    echo "=================================="
    
    # 检查依赖
    check_python
    check_pip
    
    # 创建和激活虚拟环境
    create_venv
    activate_venv
    
    # 安装依赖
    install_dependencies
    
    # 设置环境
    setup_env
    create_directories
    
    # 数据库和静态文件
    migrate_database
    collect_static
    
    # 询问是否创建超级用户
    echo -e "${YELLOW}是否创建超级用户？(y/n)${NC}"
    read -r create_admin
    if [[ "$create_admin" =~ ^[Yy]$ ]]; then
        create_superuser
    fi
    
    # 询问是否运行测试
    echo -e "${YELLOW}是否运行测试？(y/n)${NC}"
    read -r run_test
    if [[ "$run_test" =~ ^[Yy]$ ]]; then
        run_tests
    fi
    
    # 询问是否启动服务器
    echo -e "${YELLOW}是否启动开发服务器？(y/n)${NC}"
    read -r start_server
    if [[ "$start_server" =~ ^[Yy]$ ]]; then
        start_dev_server
    else
        echo -e "${GREEN}✅ 项目初始化完成！${NC}"
        echo -e "${YELLOW}💡 使用 'source venv/bin/activate' 激活虚拟环境${NC}"
        echo -e "${YELLOW}💡 使用 'python manage.py runserver' 启动服务器${NC}"
    fi
}

# 运行主函数
main "$@"