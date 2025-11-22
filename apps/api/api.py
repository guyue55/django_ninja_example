"""
Django-Ninja API 主配置

本文件定义了主要的 Ninja API 实例，包括全局配置、认证、中间件等。
"""

from ninja import NinjaAPI
from ninja.security import HttpBearer
from django.conf import settings
from django.core.exceptions import ValidationError
from typing import Optional


class AuthBearer(HttpBearer):
    """
    JWT Token 认证类
    
    通过 HTTP Bearer Token 进行身份验证，验证 JWT Token 的有效性。
    """
    
    def authenticate(self, request, token: str) -> Optional[str]:
        """
        验证 JWT Token
        
        Args:
            request: Django 请求对象
            token: JWT Token 字符串
            
        Returns:
            如果验证成功返回用户标识，失败返回 None
        """
        from apps.authentication.services import AuthService
        
        try:
            # 使用认证服务验证 Token
            user_id = AuthService.verify_token(token)
            if user_id:
                request.user_id = user_id
                return user_id
        except Exception:
            pass
        
        return None


# 创建 Ninja API 实例
api = NinjaAPI(
    # API 标题
    title='Django-Ninja API',
    
    # API 描述
    description='基于 Django-Ninja 构建的高性能 API 接口',
    
    # API 版本
    version='1.0.0',
    
    # 认证配置 - 注意：全局认证会影响所有端点
    # 我们改为在需要认证的端点上单独设置认证
    auth=None,  # 全局不设置认证，在需要的地方单独设置
    
    # URL 前缀
    # urls_namespace='api',
    
    # 文档配置
    docs_url='/docs/',  # Swagger UI 文档地址
    
    # OpenAPI 配置
    openapi_url='/openapi.json',  # OpenAPI Schema 地址
    
    # CSRF 配置 - 在测试模式下禁用CSRF
    csrf=not settings.TESTING,  # 测试模式下禁用CSRF保护
)

# 导入并添加认证路由
from apps.authentication.api import router as auth_router
api.add_router('/auth', auth_router, tags=['认证'], auth=None)

# 导入并添加用户管理路由
from apps.users.api import router as users_router
api.add_router('/users', users_router, tags=['用户管理'])

# 导入并添加健康检查路由
from apps.api.routers.health.router import router as health_router
api.add_router('/health', health_router, tags=['健康检查'], auth=None)

# 添加异常处理器
@api.exception_handler(ValidationError)
def validation_error_handler(request, exc):
    """
    Django 验证错误异常处理器
    
    处理 Django 的 ValidationError 异常，返回 422 状态码。
    """
    # 获取错误消息
    if hasattr(exc, 'message'):
        message = exc.message
    elif hasattr(exc, 'messages'):
        message = exc.messages[0] if exc.messages else "验证失败"
    else:
        message = str(exc)
    
    return api.create_response(
        request,
        {
            "error": "验证错误",
            "message": message,
            "code": 422
        },
        status=422
    )


@api.exception_handler(Exception)
def global_exception_handler(request, exc):
    """
    全局异常处理器
    
    捕获所有未处理的异常，返回统一的错误响应格式。
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    
    return api.create_response(
        request,
        {
            "error": "服务器内部错误",
            "message": "发生了未知错误，请联系管理员",
            "code": 500
        },
        status=500
    )


@api.exception_handler(ValueError)
def value_error_handler(request, exc):
    """
    值错误异常处理器
    
    处理参数验证等值错误异常。
    """
    return api.create_response(
        request,
        {
            "error": "参数错误",
            "message": str(exc),
            "code": 400
        },
        status=400
    )


