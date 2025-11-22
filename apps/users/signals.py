"""
用户信号处理器

处理用户相关的 Django 信号，如用户创建、更新、删除等事件。
"""

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import logging

# 获取用户模型
User = get_user_model()

# 配置日志
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def user_created_handler(sender, instance, created, **kwargs):
    """
    用户创建信号处理器
    
    当新用户创建时执行的操作。
    
    Args:
        sender: 发送信号的模型类
        instance: 用户实例
        created: 是否为新创建
        kwargs: 其他参数
    """
    if created:
        # 新用户创建时的操作
        logger.info(f"新用户创建: {instance.username}")
        
        # 发送欢迎邮件（异步任务更好）
        try:
            send_mail(
                subject='欢迎注册！',
                message=f'亲爱的 {instance.get_display_name()}，欢迎注册我们的平台！',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=True,
            )
            logger.info(f"欢迎邮件发送成功: {instance.email}")
        except Exception as e:
            logger.error(f"欢迎邮件发送失败: {e}")


@receiver(pre_save, sender=User)
def user_pre_save_handler(sender, instance, **kwargs):
    """
    用户保存前信号处理器
    
    在用户保存到数据库之前执行的操作。
    
    Args:
        sender: 发送信号的模型类
        instance: 用户实例
        kwargs: 其他参数
    """
    if instance.pk:
        # 更新操作
        try:
            old_user = User.objects.get(pk=instance.pk)
            
            # 检查邮箱是否变更
            if old_user.email != instance.email:
                # 如果邮箱变更，重置验证状态
                instance.email_verified = False
                logger.info(f"用户邮箱变更: {old_user.email} -> {instance.email}")
            
            # 检查手机号是否变更
            if old_user.phone_number != instance.phone_number:
                # 如果手机号变更，重置验证状态
                instance.phone_verified = False
                logger.info(f"用户手机号变更: {old_user.phone_number} -> {instance.phone_number}")
                
        except User.DoesNotExist:
            pass


@receiver(post_save, sender=User)
def user_profile_handler(sender, instance, created, **kwargs):
    """
    用户资料信号处理器
    
    确保每个用户都有对应的用户资料。
    
    Args:
        sender: 发送信号的模型类
        instance: 用户实例
        created: 是否为新创建
        kwargs: 其他参数
    """
    if created:
        # 为新用户创建资料
        try:
            from .models import UserProfile
            UserProfile.objects.get_or_create(user=instance)
            logger.info(f"用户资料创建成功: {instance.username}")
        except Exception as e:
            logger.error(f"用户资料创建失败: {e}")


@receiver(post_delete, sender=User)
def user_deleted_handler(sender, instance, **kwargs):
    """
    用户删除信号处理器
    
    当用户被删除时执行的操作。
    
    Args:
        sender: 发送信号的模型类
        instance: 被删除的用户实例
        kwargs: 其他参数
    """
    logger.info(f"用户删除: {instance.username}")
    
    # 这里可以添加用户删除后的清理操作
    # 例如：删除相关的文件、清理缓存、发送通知等


# 连接信号
# 注意：信号会在应用加载时自动连接，不需要手动调用