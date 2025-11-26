"""
认证 API 端点

提供用户认证相关的 API 接口，包括登录、登出、Token 刷新、密码重置等功能。
"""

from ninja import Router
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.utils.decorators import method_decorator
from datetime import datetime
import logging

# 导入认证类
from apps.api.api import AuthBearer

# 导入服务
from .services import AuthService

# 导入模式
from .schemas import (
    LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse,
    LogoutRequest, LogoutResponse, TokenValidationRequest, TokenValidationResponse,
    PasswordResetRequest, PasswordResetConfirm, PasswordChangeRequest,
    UserInfoResponse, RegisterRequest, RegisterResponse
)

# 获取用户模型
User = get_user_model()

# 创建路由实例
router = Router()

# 配置日志
logger = logging.getLogger(__name__)


@router.post("/login", response=LoginResponse, auth=None)
@method_decorator(csrf_exempt, name='dispatch')
def login(request, login_data: LoginRequest):
    """
    用户登录
    
    用户通过用户名、邮箱或手机号登录系统。
    
    Args:
        request: Django 请求对象
        login_data: 登录数据
        
    Returns:
        LoginResponse: 登录成功响应，包含访问令牌和用户信息
        
    Raises:
        ValidationError: 当登录失败时抛出
    """
    try:
        # 用户认证
        user = AuthService.authenticate_user(login_data.username, login_data.password)
        
        if not user:
            raise ValidationError("用户名或密码错误")
        
        # 生成令牌
        token_data = AuthService.generate_tokens(user)
        
        # 建立Django会话登录（用于模板中的 user.is_authenticated）
        try:
            django_login(request, user)
        except Exception:
            pass
        
        # 更新最后登录IP
        ip_address = request.META.get('REMOTE_ADDR')
        user.update_last_login_info(ip_address)
        
        logger.info(f"用户登录成功: {user.username}")
        
        return LoginResponse(
            access_token=token_data['access_token'],
            refresh_token=token_data['refresh_token'],
            token_type=token_data['token_type'],
            expires_in=token_data['expires_in'],
            user_id=user.id
        )
        
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"用户登录失败: {e}", exc_info=True)
        raise ValidationError("登录失败，请稍后重试")


@router.post("/refresh", response=RefreshTokenResponse, auth=None)
def refresh_token(request, refresh_data: RefreshTokenRequest):
    """
    刷新访问令牌
    
    使用刷新令牌获取新的访问令牌。
    
    Args:
        request: Django 请求对象
        refresh_data: 刷新令牌数据
        
    Returns:
        RefreshTokenResponse: 新的访问令牌信息
        
    Raises:
        ValidationError: 当刷新失败时抛出
    """
    try:
        # 验证刷新令牌并生成新的访问令牌
        token_data = AuthService.refresh_access_token(refresh_data.refresh_token)
        
        if not token_data:
            raise ValidationError("刷新令牌无效或已过期")
        
        return RefreshTokenResponse(
            access_token=token_data['access_token'],
            token_type=token_data['token_type'],
            expires_in=token_data['expires_in']
        )
        
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"令牌刷新失败: {e}")
        raise ValidationError("令牌刷新失败，请重新登录")


@router.post("/logout", response=LogoutResponse, auth=AuthBearer())
def logout(request, logout_data: LogoutRequest):
    """
    用户登出
    
    用户登出系统，清除认证状态。
    
    Args:
        request: Django 请求对象
        logout_data: 登出数据（可选刷新令牌）
        
    Returns:
        LogoutResponse: 登出成功响应
    """
    try:
        # 获取当前用户ID
        user_id = getattr(request, 'user_id', None)
        
        if user_id:
            # 执行登出操作
            refresh_token = logout_data.refresh_token if logout_data.refresh_token else None
            AuthService.logout_user(user_id, refresh_token)
            try:
                django_logout(request)
            except Exception:
                pass
            logger.info(f"用户登出成功: {user_id}")
        
        return LogoutResponse(message="登出成功")
        
    except Exception as e:
        logger.error(f"用户登出失败: {e}")
        return LogoutResponse(message="登出失败")


@router.post("/validate", response=TokenValidationResponse, auth=None)
def validate_token(request, validation_data: TokenValidationRequest):
    """
    验证访问令牌
    
    验证访问令牌的有效性。
    
    Args:
        request: Django 请求对象
        validation_data: 令牌验证数据
        
    Returns:
        TokenValidationResponse: 令牌验证结果
    """
    try:
        # 验证 Token 格式
        if not AuthService.validate_token_format(validation_data.token):
            return TokenValidationResponse(valid=False)
        
        # 验证 Token 有效性
        user_id = AuthService.verify_token(validation_data.token)
        
        if user_id:
            # 获取 Token 过期时间
            import jwt
            payload = jwt.decode(
                validation_data.token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            expires_at = datetime.fromtimestamp(payload['exp']).isoformat()
            
            return TokenValidationResponse(
                valid=True,
                user_id=user_id,
                expires_at=expires_at
            )
        else:
            return TokenValidationResponse(valid=False)
            
    except Exception as e:
        logger.error(f"令牌验证失败: {e}")
        return TokenValidationResponse(valid=False)


@router.get("/me", response=UserInfoResponse, auth=AuthBearer())
def get_current_user_info(request):
    """
    获取当前用户信息
    
    获取当前认证用户的基本信息。
    
    Args:
        request: Django 请求对象
        
    Returns:
        UserInfoResponse: 当前用户信息
        
    Raises:
        ValidationError: 当用户不存在时抛出
    """
    try:
        # 获取当前用户ID
        user_id = getattr(request, 'user_id', None)
        
        if not user_id:
            raise ValidationError("用户未认证")
        
        # 获取用户信息
        user = User.objects.get(id=user_id, is_deleted=False)
        
        return UserInfoResponse(
            user_id=user.id,
            username=user.username,
            email=user.email,
            nickname=user.nickname,
            user_type=user.user_type,
            status=user.status,
            email_verified=user.email_verified,
            phone_verified=user.phone_verified
        )
        
    except User.DoesNotExist:
        raise ValidationError("用户不存在")
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        raise ValidationError("获取用户信息失败")


@router.post("/password/reset", response=dict, auth=None)
def request_password_reset(request, reset_data: PasswordResetRequest):
    """
    请求密码重置
    
    发送密码重置邮件到用户邮箱。
    
    Args:
        request: Django 请求对象
        reset_data: 密码重置请求数据
        
    Returns:
        dict: 操作结果消息
    """
    try:
        # 查找用户
        user = User.objects.filter(email=reset_data.email, is_deleted=False).first()
        
        if not user:
            # 为了安全，不暴露用户是否存在
            return {"message": "如果邮箱存在，重置邮件已发送"}
        
        # 生成重置令牌
        reset_token = AuthService.generate_password_reset_token(user)
        
        # 发送重置邮件（这里简化处理，实际应该使用异步任务）
        try:
            reset_url = f"{request.build_absolute_uri('/')}auth/password/reset/confirm?token={reset_token}"
            send_mail(
                subject='密码重置请求',
                message=f'请点击以下链接重置您的密码：{reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
            logger.info(f"密码重置邮件发送成功: {user.email}")
        except Exception as e:
            logger.error(f"密码重置邮件发送失败: {e}")
        
        return {"message": "如果邮箱存在，重置邮件已发送"}
        
    except Exception as e:
        logger.error(f"密码重置请求失败: {e}")
        return {"message": "密码重置请求失败，请稍后重试"}


@router.post("/password/reset/confirm", response=dict, auth=None)
def confirm_password_reset(request, reset_data: PasswordResetConfirm):
    """
    确认密码重置
    
    使用重置令牌设置新密码。
    
    Args:
        request: Django 请求对象
        reset_data: 密码重置确认数据
        
    Returns:
        dict: 操作结果消息
    """
    try:
        # 验证并重置密码
        success = AuthService.reset_user_password(reset_data.token, reset_data.new_password)
        
        if success:
            return {"message": "密码重置成功"}
        else:
            raise ValidationError("密码重置失败，令牌可能已过期")
            
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"密码重置失败: {e}")
        raise ValidationError("密码重置失败，请稍后重试")


@router.post("/password/change", response=dict, auth=AuthBearer())
def change_password(request, change_data: PasswordChangeRequest):
    """
    修改密码
    
    已登录用户修改密码。
    
    Args:
        request: Django 请求对象
        change_data: 密码修改数据
        
    Returns:
        dict: 操作结果消息
        
    Raises:
        ValidationError: 当密码修改失败时抛出
    """
    try:
        # 获取当前用户ID
        user_id = getattr(request, 'user_id', None)
        
        if not user_id:
            raise ValidationError("用户未认证")
        
        # 获取用户
        user = User.objects.get(id=user_id, is_deleted=False)
        
        # 更新密码
        success = UserService.update_password(
            user,
            change_data.old_password,
            change_data.new_password
        )
        
        if success:
            # 登出用户（可选）
            AuthService.logout_user(user_id)
            return {"message": "密码修改成功，请重新登录"}
        else:
            raise ValidationError("密码修改失败")
            
    except User.DoesNotExist:
        raise ValidationError("用户不存在")
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"密码修改失败: {e}")
        raise ValidationError("密码修改失败，请稍后重试")