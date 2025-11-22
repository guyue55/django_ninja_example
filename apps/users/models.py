"""
用户模型定义

定义用户数据模型，扩展 Django 内置的 AbstractUser 模型，添加自定义字段和方法。
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    用户模型
    
    扩展 Django 内置用户模型，添加自定义字段和业务逻辑。
    """
    
    # 用户类型选择
    USER_TYPE_CHOICES = [
        ('regular', '普通用户'),
        ('admin', '管理员'),
        ('superuser', '超级管理员'),
    ]
    
    # 用户状态选择
    STATUS_CHOICES = [
        ('active', '活跃'),
        ('inactive', '非活跃'),
        ('suspended', '暂停'),
        ('deleted', '已删除'),
    ]
    
    # 用户类型
    user_type = models.CharField(
        verbose_name='用户类型',
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='regular'
    )
    
    # 用户状态
    status = models.CharField(
        verbose_name='用户状态',
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # 昵称
    nickname = models.CharField(
        verbose_name='昵称',
        max_length=50,
        blank=True,
        help_text='用户昵称，可用于显示'
    )
    
    # 头像
    avatar = models.ImageField(
        verbose_name='头像',
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        help_text='用户头像图片'
    )
    
    # 手机号
    phone_regex = RegexValidator(
        regex=r'^1[3-9]\d{9}$',
        message='请输入有效的手机号码'
    )
    phone_number = models.CharField(
        verbose_name='手机号码',
        validators=[phone_regex],
        max_length=11,
        blank=True,
        unique=True,
        null=True,
        help_text='用户手机号码，用于登录和通知'
    )
    
    # 生日
    birth_date = models.DateField(
        verbose_name='生日',
        blank=True,
        null=True,
        help_text='用户生日'
    )
    
    # 个人简介
    bio = models.TextField(
        verbose_name='个人简介',
        max_length=500,
        blank=True,
        help_text='用户个人简介，最多500字'
    )
    
    # 时区
    timezone = models.CharField(
        verbose_name='时区',
        max_length=50,
        default='Asia/Shanghai',
        help_text='用户所在时区'
    )
    
    # 语言
    language = models.CharField(
        verbose_name='语言',
        max_length=10,
        default='zh-hans',
        help_text='用户偏好语言'
    )
    
    # 邮箱验证状态
    email_verified = models.BooleanField(
        verbose_name='邮箱已验证',
        default=False,
        help_text='用户邮箱是否已通过验证'
    )
    
    # 手机验证状态
    phone_verified = models.BooleanField(
        verbose_name='手机已验证',
        default=False,
        help_text='用户手机是否已通过验证'
    )
    
    # 最后登录IP
    last_login_ip = models.GenericIPAddressField(
        verbose_name='最后登录IP',
        blank=True,
        null=True,
        help_text='用户最后登录的IP地址'
    )
    
    # 注册IP
    registration_ip = models.GenericIPAddressField(
        verbose_name='注册IP',
        blank=True,
        null=True,
        help_text='用户注册时的IP地址'
    )
    
    # 元数据
    metadata = models.JSONField(
        verbose_name='元数据',
        default=dict,
        blank=True,
        help_text='用户相关的额外元数据信息'
    )
    
    # 软删除标记
    is_deleted = models.BooleanField(
        verbose_name='已删除',
        default=False,
        help_text='软删除标记，标记为删除的用户不会真正删除'
    )
    
    # 删除时间
    deleted_at = models.DateTimeField(
        verbose_name='删除时间',
        blank=True,
        null=True,
        help_text='用户被软删除的时间'
    )
    
    # 创建时间
    created_at = models.DateTimeField(
        verbose_name='创建时间',
        auto_now_add=True,
        help_text='用户创建时间'
    )
    
    # 更新时间
    updated_at = models.DateTimeField(
        verbose_name='更新时间',
        auto_now=True,
        help_text='用户信息最后更新时间'
    )
    
    class Meta:
        """模型元数据"""
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['status']),
            models.Index(fields=['user_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        """
        字符串表示
        
        Returns:
            str: 用户的字符串表示，优先显示昵称，然后是用户名
        """
        return self.nickname or self.username
    
    def soft_delete(self):
        """
        软删除用户
        
        标记用户为已删除状态，而不是真正从数据库中删除。
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.status = 'deleted'
        self.save(update_fields=['is_deleted', 'deleted_at', 'status'])
    
    def restore(self):
        """
        恢复软删除的用户
        
        取消用户的软删除状态。
        """
        self.is_deleted = False
        self.deleted_at = None
        self.status = 'active'
        self.save(update_fields=['is_deleted', 'deleted_at', 'status'])
    
    def is_fully_verified(self):
        """
        检查用户是否完全验证
        
        检查用户的邮箱和手机是否都已验证。
        
        Returns:
            bool: 如果邮箱和手机都已验证返回 True，否则返回 False
        """
        return self.email_verified and self.phone_verified
    
    def get_display_name(self):
        """
        获取显示名称
        
        获取用于显示的用户名称，优先级：昵称 > 用户名 > 邮箱
        
        Returns:
            str: 用户的显示名称
        """
        return self.nickname or self.username or self.email
    
    def update_last_login_info(self, ip_address):
        """
        更新最后登录信息
        
        更新用户的最后登录时间和 IP 地址。
        
        Args:
            ip_address (str): 登录 IP 地址
        """
        self.last_login_ip = ip_address
        self.last_login = timezone.now()  # 显式更新最后登录时间
        self.save(update_fields=['last_login_ip', 'last_login'])


class UserProfile(models.Model):
    """
    用户扩展资料模型
    
    存储用户的详细个人资料信息，与用户模型一对一关联。
    """
    
    # 性别选择
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
        ('O', '其他'),
        ('N', '不愿透露'),
    ]
    
    # 关联用户
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='用户'
    )
    
    # 性别
    gender = models.CharField(
        verbose_name='性别',
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        help_text='用户性别'
    )
    
    # 职业
    occupation = models.CharField(
        verbose_name='职业',
        max_length=100,
        blank=True,
        help_text='用户职业'
    )
    
    # 公司
    company = models.CharField(
        verbose_name='公司',
        max_length=200,
        blank=True,
        help_text='用户所在公司'
    )
    
    # 地址
    address = models.TextField(
        verbose_name='地址',
        max_length=500,
        blank=True,
        help_text='用户地址信息'
    )
    
    # 个人网站
    website = models.URLField(
        verbose_name='个人网站',
        blank=True,
        help_text='用户个人网站或博客'
    )
    
    # 社交媒体链接
    social_links = models.JSONField(
        verbose_name='社交媒体链接',
        default=dict,
        blank=True,
        help_text='用户社交媒体链接，如微博、GitHub等'
    )
    
    # 兴趣爱好
    interests = models.TextField(
        verbose_name='兴趣爱好',
        max_length=1000,
        blank=True,
        help_text='用户兴趣爱好'
    )
    
    # 个人标签
    tags = models.JSONField(
        verbose_name='个人标签',
        default=list,
        blank=True,
        help_text='用户个人标签，用于个性化推荐'
    )
    
    # 隐私设置
    privacy_settings = models.JSONField(
        verbose_name='隐私设置',
        default=dict,
        blank=True,
        help_text='用户隐私设置，控制信息公开程度'
    )
    
    # 创建时间
    created_at = models.DateTimeField(
        verbose_name='创建时间',
        auto_now_add=True
    )
    
    # 更新时间
    updated_at = models.DateTimeField(
        verbose_name='更新时间',
        auto_now=True
    )
    
    class Meta:
        """模型元数据"""
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
        db_table = 'user_profiles'
    
    def __str__(self):
        """
        字符串表示
        
        Returns:
            str: 用户资料的字符串表示
        """
        return f"{self.user.get_display_name()} 的资料"
    
    def get_privacy_setting(self, key, default=True):
        """
        获取隐私设置
        
        Args:
            key (str): 隐私设置键名
            default (bool): 默认值
            
        Returns:
            bool: 隐私设置值
        """
        return self.privacy_settings.get(key, default)