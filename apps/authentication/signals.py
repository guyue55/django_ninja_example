"""
认证信号处理器

处理认证相关的 Django 信号，如用户登录、登出、密码修改等事件。
"""

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings
import logging

# 获取用户模型
User = get_user_model()

# 配置日志
logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    """
    用户登录成功信号处理器
    
    当用户成功登录时执行的操作。
    
    Args:
        sender: 发送信号的模型类
        request: 请求对象
        user: 登录的用户实例
        kwargs: 其他参数
    """
    # 记录登录IP
    ip_address = request.META.get('REMOTE_ADDR') if request else '未知'
    user.update_last_login_info(ip_address)
    
    logger.info(f"用户登录成功: {user.username} (IP: {ip_address})")
    
    # 可以在这里添加登录统计、发送通知等操作


@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    """
    用户登出成功信号处理器
    
    当用户成功登出时执行的操作。
    
    Args:
        sender: 发送信号的模型类
        request: 请求对象
        user: 登出的用户实例
        kwargs: 其他参数
    """
    logger.info(f"用户登出成功: {user.username if user else '匿名用户'}")
    
    # 可以在这里添加登出清理操作


@receiver(user_login_failed)
def user_login_failed_handler(sender, credentials, request, **kwargs):
    """
    用户登录失败信号处理器
    
    当用户登录失败时执行的操作。
    
    Args:
        sender: 发送信号的模型类
        credentials: 登录凭据
        request: 请求对象
        kwargs: 其他参数
    """
    username = credentials.get('username', '未知用户')
    ip_address = request.META.get('REMOTE_ADDR') if request else '未知'
    
    logger.warning(f"用户登录失败: {username} (IP: {ip_address})")
    
    # 可以在这里添加登录失败统计、安全告警等操作
    # 例如：记录失败次数，达到一定次数后锁定账户


@receiver(pre_save, sender=User)
def password_change_handler(sender, instance, **kwargs):
    """
    密码修改信号处理器
    
    当用户密码被修改时执行的操作。
    
    Args:
        sender: 发送信号的模型类
        instance: 用户实例
        kwargs: 其他参数
    """
    if instance.pk:
        try:
            old_user = User.objects.get(pk=instance.pk)
            
            # 检查密码是否变更
            if old_user.password != instance.password:
                logger.info(f"用户密码修改: {instance.username}")
                
                # 可以在这里添加密码修改通知等操作
                # 例如：发送邮件通知用户密码已修改
                
        except User.DoesNotExist:
            pass


# 连接信号
# 注意：信号会在应用加载时自动连接，不需要手动调用