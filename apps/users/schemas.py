"""
用户相关数据模式

定义用户相关的 Pydantic 模型，用于 API 请求和响应的数据验证与序列化。
"""

from ninja import Schema
from ninja import FilterSchema
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field, EmailStr, validator


class UserBase(Schema):
    """用户基础模式"""
    username: str = Field(..., min_length=3, max_length=150, description='用户名')
    email: EmailStr = Field(..., description='邮箱地址')
    nickname: Optional[str] = Field(None, max_length=50, description='昵称')
    phone_number: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description='手机号码')


class UserCreate(UserBase):
    """用户创建模式"""
    password: str = Field(..., min_length=8, max_length=128, description='密码')
    password_confirm: str = Field(..., min_length=8, max_length=128, description='确认密码')
    
    @validator('password_confirm')
    def passwords_match(cls, v, values):
        """验证密码是否匹配"""
        if 'password' in values and v != values['password']:
            raise ValueError('两次输入的密码不一致')
        return v
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """验证用户名格式"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        return v.lower()


class UserUpdate(Schema):
    """用户更新模式"""
    nickname: Optional[str] = Field(None, max_length=50, description='昵称')
    email: Optional[EmailStr] = Field(None, description='邮箱地址')
    phone_number: Optional[str] = Field(None, pattern=r'^1[3-9]\d{9}$', description='手机号码')
    birth_date: Optional[datetime] = Field(None, description='生日')
    bio: Optional[str] = Field(None, max_length=500, description='个人简介')
    timezone: Optional[str] = Field(None, description='时区')
    language: Optional[str] = Field(None, description='语言')
    avatar: Optional[str] = Field(None, description='头像URL')


class UserPasswordUpdate(Schema):
    """用户密码更新模式"""
    old_password: str = Field(..., min_length=1, description='当前密码')
    new_password: str = Field(..., min_length=8, max_length=128, description='新密码')
    new_password_confirm: str = Field(..., min_length=8, max_length=128, description='确认新密码')
    
    @validator('new_password_confirm')
    def passwords_match(cls, v, values):
        """验证新密码是否匹配"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的新密码不一致')
        return v


class UserResponse(UserBase):
    """用户响应模式"""
    id: int = Field(..., description='用户ID')
    user_type: str = Field(..., description='用户类型')
    status: str = Field(..., description='用户状态')
    email_verified: bool = Field(..., description='邮箱是否验证')
    phone_verified: bool = Field(..., description='手机是否验证')
    avatar_url: Optional[str] = Field(None, description='头像URL')
    bio: Optional[str] = Field(None, description='个人简介')
    last_login: Optional[datetime] = Field(None, description='最后登录时间')
    created_at: datetime = Field(..., description='创建时间')
    updated_at: datetime = Field(..., description='更新时间')
    
    class Config:
        """Pydantic 配置"""
        from_attributes = True  # 支持从 ORM 模型转换


class UserListResponse(Schema):
    """用户列表响应模式"""
    items: List[UserResponse] = Field(..., description='用户列表')
    total: int = Field(..., description='总记录数')
    page: int = Field(..., description='当前页码')
    page_size: int = Field(..., description='每页记录数')
    total_pages: int = Field(..., description='总页数')


class UserFilter(FilterSchema):
    """用户过滤模式"""
    username: Optional[str] = Field(None, description='用户名（模糊匹配）')
    email: Optional[str] = Field(None, description='邮箱（模糊匹配）')
    nickname: Optional[str] = Field(None, description='昵称（模糊匹配）')
    user_type: Optional[str] = Field(None, description='用户类型')
    status: Optional[str] = Field(None, description='用户状态')
    email_verified: Optional[bool] = Field(None, description='邮箱验证状态')
    phone_verified: Optional[bool] = Field(None, description='手机验证状态')
    created_at_start: Optional[datetime] = Field(None, description='创建时间开始')
    created_at_end: Optional[datetime] = Field(None, description='创建时间结束')


class UserProfileBase(Schema):
    """用户资料基础模式"""
    gender: Optional[str] = Field(None, description='性别')
    occupation: Optional[str] = Field(None, max_length=100, description='职业')
    company: Optional[str] = Field(None, max_length=200, description='公司')
    address: Optional[str] = Field(None, max_length=500, description='地址')
    website: Optional[str] = Field(None, description='个人网站')
    interests: Optional[str] = Field(None, max_length=1000, description='兴趣爱好')


class UserProfileCreate(UserProfileBase):
    """用户资料创建模式"""
    pass


class UserProfileUpdate(UserProfileBase):
    """用户资料更新模式"""
    social_links: Optional[Dict[str, str]] = Field(None, description='社交媒体链接')
    tags: Optional[List[str]] = Field(None, description='个人标签')
    privacy_settings: Optional[Dict[str, Any]] = Field(None, description='隐私设置')


class UserProfileResponse(UserProfileBase):
    """用户资料响应模式"""
    id: int = Field(..., description='资料ID')
    user_id: int = Field(..., description='用户ID')
    social_links: Dict[str, str] = Field(default_factory=dict, description='社交媒体链接')
    tags: List[str] = Field(default_factory=list, description='个人标签')
    privacy_settings: Dict[str, Any] = Field(default_factory=dict, description='隐私设置')
    created_at: datetime = Field(..., description='创建时间')
    updated_at: datetime = Field(..., description='更新时间')
    
    class Config:
        """Pydantic 配置"""
        from_attributes = True


class UserDetailResponse(Schema):
    """用户详情响应模式"""
    user: UserResponse = Field(..., description='用户信息')
    profile: Optional[UserProfileResponse] = Field(None, description='用户资料')


class UserLoginRequest(Schema):
    """用户登录请求模式"""
    username: str = Field(..., description='用户名或邮箱')
    password: str = Field(..., description='密码')
    remember_me: bool = Field(False, description='记住登录状态')


class UserLoginResponse(Schema):
    """用户登录响应模式"""
    access_token: str = Field(..., description='访问令牌')
    refresh_token: str = Field(..., description='刷新令牌')
    token_type: str = Field('Bearer', description='令牌类型')
    expires_in: int = Field(..., description='令牌过期时间（秒）')
    user: UserResponse = Field(..., description='用户信息')


class UserRegisterRequest(UserCreate):
    """用户注册请求模式"""
    pass


class UserRegisterResponse(Schema):
    """用户注册响应模式"""
    message: str = Field(..., description='注册成功消息')
    user: UserResponse = Field(..., description='新用户信息')


class PasswordResetRequest(Schema):
    """密码重置请求模式"""
    email: EmailStr = Field(..., description='注册邮箱')


class PasswordResetConfirm(Schema):
    """密码重置确认模式"""
    token: str = Field(..., description='重置令牌')
    new_password: str = Field(..., min_length=8, max_length=128, description='新密码')
    new_password_confirm: str = Field(..., min_length=8, max_length=128, description='确认新密码')
    
    @validator('new_password_confirm')
    def passwords_match(cls, v, values):
        """验证新密码是否匹配"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的新密码不一致')
        return v


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