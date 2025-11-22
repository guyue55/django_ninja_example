# Python 基础镜像
FROM python:3.8-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    APP_HOME=/app

# 设置工作目录
WORKDIR $APP_HOME

# 安装系统依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        netcat-traditional \
        curl \
        gettext \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
COPY requirements/ requirements/

# 安装 Python 依赖
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

# 复制项目代码
COPY . .

# 创建必要的目录
RUN mkdir -p logs media staticfiles

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 创建非 root 用户
RUN groupadd -r django && useradd -r -g django django \
    && chown -R django:django $APP_HOME

# 切换到非 root 用户
USER django

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]