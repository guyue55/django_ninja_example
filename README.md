# Django-Ninja 项目模板

这是一个基于 Django 和 Django-Ninja 的高性能 API 项目模板，遵循最佳实践和 Google Python Style Guide。

## 🚀 功能特性

- **高性能 API**: 基于 Django-Ninja 构建，提供类型安全和自动文档生成
- **完整的用户系统**: 用户注册、登录、认证、授权、资料管理
- **JWT 认证**: 支持访问令牌和刷新令牌的完整认证体系
- **数据库支持**: 支持 PostgreSQL、MySQL、SQLite 等多种数据库
- **缓存支持**: 集成 Redis 缓存，提升系统性能
- **文件上传**: 支持头像、文档等文件上传功能
- **权限管理**: 基于角色的权限控制系统
- **API 文档**: 自动生成 Swagger/OpenAPI 文档
- **测试覆盖**: 完整的单元测试和集成测试
- **容器化**: Docker 容器化部署支持
- **生产就绪**: 包含安全、监控、日志等生产环境配置

## 📋 系统要求

- Python 3.8+
- Django 4.2+
- PostgreSQL 12+ (推荐) 或 SQLite (开发)
- Redis 6+ (可选，用于缓存)

## 🛠️ 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd django_ninja_template

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 环境配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，设置必要的配置
# 特别注意修改 SECRET_KEY 和数据库配置
```

### 3. 数据库设置

```bash
# 运行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

### 4. 启动服务

```bash
# 开发服务器
python manage.py runserver

# 访问 API 文档
# http://localhost:8000/api/docs/
```

## 📚 API 文档

启动服务后，可以通过以下地址访问 API 文档：

- **Swagger UI**: http://localhost:8000/api/docs/
- **OpenAPI Schema**: http://localhost:8000/api/openapi.json

## 🔧 项目结构

```
django_ninja_template/
├── apps/                    # Django 应用
│   ├── api/                # API 核心配置
│   ├── auth/               # 认证授权
│   └── users/              # 用户管理
├── config/                 # Django 配置
│   ├── settings.py         # 主配置文件
│   ├── urls.py            # URL 路由配置
│   └── wsgi.py            # WSGI 配置
├── utils/                  # 工具函数
├── tests/                  # 测试文件
├── deployments/            # 部署配置
│   ├── docker/            # Docker 配置
│   └── k8s/               # Kubernetes 配置
├── requirements.txt       # Python 依赖
├── manage.py              # Django 管理脚本
└── pytest.ini            # 测试配置
```

## 🔐 认证机制

项目使用 JWT (JSON Web Token) 进行身份认证：

### 登录获取令牌

```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

响应示例：
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 86400,
    "user_id": 1
}
```

### 使用令牌访问 API

在请求头中添加认证信息：
```http
Authorization: Bearer your_access_token
```

### 刷新访问令牌

```http
POST /api/auth/refresh/
Content-Type: application/json

{
    "refresh_token": "your_refresh_token"
}
```

## 👥 用户管理

### 用户注册

```http
POST /api/users/register/
Content-Type: application/json

{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "nickname": "新用户"
}
```

### 获取用户信息

```http
GET /api/users/me/
Authorization: Bearer your_access_token
```

### 更新用户信息

```http
PUT /api/users/me/
Authorization: Bearer your_access_token
Content-Type: application/json

{
    "nickname": "Updated Nickname",
    "bio": "Updated bio"
}
```

## 🧪 测试

运行测试套件：

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_user_models.py

# 运行测试并生成覆盖率报告
pytest --cov=apps --cov-report=html

# 运行测试并显示详细输出
pytest -v
```

## 🐳 Docker 部署

### 开发环境

```bash
# 启动服务
cd deployments/docker
docker-compose up -d

# 查看日志
docker-compose logs -f web

# 停止服务
docker-compose down
```

### 生产环境

```bash
# 复制生产环境配置
cp .env.example .env

# 编辑 .env 文件，设置生产环境配置

# 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f web

# 停止服务
docker-compose -f docker-compose.prod.yml down
```

## 📊 监控和健康检查

项目包含健康检查端点：

```http
GET /api/health/
```

返回系统状态信息，包括数据库和缓存连接状态。

详细健康检查：
```http
GET /api/health/detailed/
```

返回详细的系统状态，包括资源使用情况。

## 🔧 环境配置

### 开发环境 (.env.development)

```env
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://127.0.0.1:6379/1
```

### 生产环境 (.env.production)

```env
DEBUG=False
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/1
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
```

## 📈 性能优化

- **数据库优化**: 使用连接池、索引优化、查询优化
- **缓存策略**: Redis 缓存、HTTP 缓存、数据库查询缓存
- **静态文件**: 使用 CDN、文件压缩、浏览器缓存
- **API 优化**: 分页、字段过滤、数据序列化优化

## 🔒 安全特性

- **密码安全**: 使用 PBKDF2 算法加密存储
- **JWT 安全**: 密钥管理、过期时间控制、令牌刷新
- **CSRF 保护**: Django 内置 CSRF 保护
- **SQL 注入防护**: ORM 参数化查询
- **XSS 防护**: 输入验证、输出转义
- **HTTPS 支持**: 生产环境强制 HTTPS
- **安全头**: X-Frame-Options、X-Content-Type-Options 等

## 📚 扩展功能

### 添加新的 API 模块

1. 创建新的 Django 应用：
```bash
python manage.py startapp myapp apps/myapp
```

2. 创建 API 路由和模式：
```python
# apps/myapp/api.py
from ninja import Router
from ninja import Schema

router = Router()

class MyResponse(Schema):
    message: str

@router.get("/hello", response=MyResponse)
def hello(request):
    return {"message": "Hello World"}
```

3. 注册到主 API：
```python
# apps/api/api.py
api.add_router("/myapp", "apps.myapp.api.router", tags=["我的应用"])
```

### 添加自定义权限

```python
# apps/auth/permissions.py
from ninja.security import HttpBearer

class CustomPermission(HttpBearer):
    def authenticate(self, request, token):
        # 自定义权限逻辑
        if token == "special_token":
            return token
        return None
```

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

如果你遇到问题或有建议，请通过以下方式联系我们：

- 创建 Issue
- 发送邮件到: support@example.com
- 访问文档: https://docs.example.com

## 🎉 致谢

- [Django](https://www.djangoproject.com/) - 强大的 Web 框架
- [Django-Ninja](https://django-ninja.rest-framework.com/) - 高性能 API 框架
- [PostgreSQL](https://www.postgresql.org/) - 强大的关系型数据库
- [Redis](https://redis.io/) - 高性能缓存数据库

---

⭐ 如果这个项目对你有帮助，请给个 Star！