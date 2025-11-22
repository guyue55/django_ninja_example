"""
认证相关数据模式

定义认证相关的 Pydantic 模型，用于 API 请求和响应的数据验证与序列化。
"""

from ninja import Schema
from typing import Optional
from pydantic import Field, EmailStr


class LoginRequest(Schema):
    """登录请求模式"""
    username: str = Field(..., description='用户名、邮箱或手机号')
    password: str = Field(..., description='密码')
    remember_me: bool = Field(False, description='记住登录状态')


class LoginResponse(Schema):
    """登录响应模式"""
    access_token: str = Field(..., description='访问令牌')
    refresh_token: str = Field(..., description='刷新令牌')
    token_type: str = Field('Bearer', description='令牌类型')
    expires_in: int = Field(..., description='令牌过期时间（秒）')
    user_id: int = Field(..., description='用户ID')


class RefreshTokenRequest(Schema):
    """刷新令牌请求模式"""
    refresh_token: str = Field(..., description='刷新令牌')


class RefreshTokenResponse(Schema):
    """刷新令牌响应模式"""
    access_token: str = Field(..., description='新的访问令牌')
    token_type: str = Field('Bearer', description='令牌类型')
    expires_in: int = Field(..., description='令牌过期时间（秒）')


class LogoutRequest(Schema):
    """登出请求模式"""
    refresh_token: Optional[str] = Field(None, description='刷新令牌（可选）')


class LogoutResponse(Schema):
    """登出响应模式"""
    message: str = Field(..., description='登出成功消息')


class PasswordResetRequest(Schema):
    """密码重置请求模式"""
    email: EmailStr = Field(..., description='注册邮箱')


class PasswordResetConfirm(Schema):
    """密码重置确认模式"""
    token: str = Field(..., description='重置令牌')
    new_password: str = Field(..., min_length=8, max_length=128, description='新密码')
    new_password_confirm: str = Field(..., min_length=8, max_length=128, description='确认新密码')
    
    def validate_passwords_match(cls, v, values):
        """验证新密码是否匹配"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的新密码不一致')
        return v


class PasswordChangeRequest(Schema):
    """密码修改请求模式"""
    old_password: str = Field(..., description='当前密码')
    new_password: str = Field(..., min_length=8, max_length=128, description='新密码')
    new_password_confirm: str = Field(..., min_length=8, max_length=128, description='确认新密码')
    
    def validate_passwords_match(cls, v, values):
        """验证新密码是否匹配"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的新密码不一致')
        return v


class TokenValidationRequest(Schema):
    """令牌验证请求模式"""
    token: str = Field(..., description='要验证的令牌')


class TokenValidationResponse(Schema):
    """令牌验证响应模式"""
    valid: bool = Field(..., description='令牌是否有效')
    user_id: Optional[int] = Field(None, description='用户ID（如果有效）')
    expires_at: Optional[str] = Field(None, description='过期时间（如果有效）')


class UserInfoResponse(Schema):
    """用户信息响应模式"""
    user_id: int = Field(..., description='用户ID')
    username: str = Field(..., description='用户名')
    email: str = Field(..., description='邮箱')
    nickname: Optional[str] = Field(None, description='昵称')
    user_type: str = Field(..., description='用户类型')
    status: str = Field(..., description='用户状态')
    email_verified: bool = Field(..., description='邮箱验证状态')
    phone_verified: bool = Field(..., description='手机验证状态')


class RegisterRequest(Schema):
    """注册请求模式"""
    username: str = Field(..., min_length=3, max_length=150, description='用户名')
    email: EmailStr = Field(..., description='邮箱地址')
    password: str = Field(..., min_length=8, max_length=128, description='密码')
    password_confirm: str = Field(..., min_length=8, max_length=128, description='确认密码')
    nickname: Optional[str] = Field(None, max_length=50, description='昵称')
    phone_number: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description='手机号码')
    
    def validate_passwords_match(cls, v, values):
        """验证密码是否匹配"""
        if 'password' in values and v != values['password']:
            raise ValueError('两次输入的密码不一致')
        return v
    
    def validate_username_format(cls, v):
        """验证用户名格式"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        return v.lower()


class RegisterResponse(Schema):
    """注册响应模式"""
    message: str = Field(..., description='注册成功消息')
    user_id: int = Field(..., description='新用户ID')
    access_token: str = Field(..., description='访问令牌')
    refresh_token: str = Field(..., description='刷新令牌')


class EmailVerificationRequest(Schema):
    """邮箱验证请求模式"""
    email: EmailStr = Field(..., description='待验证邮箱')


class EmailVerificationConfirm(Schema):
    """邮箱验证确认模式"""
    token: str = Field(..., description='验证令牌')


class PhoneVerificationRequest(Schema):
    """手机验证请求模式"""
    phone_number: str = Field(..., pattern=r'^1[3-9]\d{9}$', description='手机号码')


class PhoneVerificationConfirm(Schema):
    """手机验证确认模式"""
    phone_number: str = Field(..., pattern=r'^1[3-9]\d{9}$', description='手机号码')
    code: str = Field(..., min_length=4, max_length=6, description='验证码')