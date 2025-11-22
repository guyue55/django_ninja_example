"""
用户业务逻辑服务

包含用户相关的业务逻辑处理，如用户创建、更新、验证等操作。
"""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from typing import Optional, Dict, Any
import logging

# 获取用户模型
User = get_user_model()

# 配置日志
logger = logging.getLogger(__name__)


class UserService:
    """
    用户服务类
    
    提供用户相关的业务逻辑处理方法。
    """
    
    @staticmethod
    @transaction.atomic
    def create_user(user_data: Dict[str, Any]) -> User:
        """
        创建新用户
        
        Args:
            user_data: 用户数据字典，包含用户名、邮箱、密码等
            
        Returns:
            User: 创建的用户实例
            
        Raises:
            ValidationError: 当数据验证失败时抛出
        """
        try:
            # 验证密码
            validate_password(user_data['password'])
            
            # 检查用户名是否已存在
            if User.objects.filter(username=user_data['username']).exists():
                raise ValidationError(f"用户名 '{user_data['username']}' 已存在")
            
            # 检查邮箱是否已存在
            if User.objects.filter(email=user_data['email']).exists():
                raise ValidationError(f"邮箱 '{user_data['email']}' 已存在")
            
            # 创建用户
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password']
            )
            
            # 设置可选字段
            optional_fields = ['nickname', 'phone_number', 'birth_date', 'bio', 'timezone', 'language']
            for field in optional_fields:
                if field in user_data and user_data[field] is not None:
                    setattr(user, field, user_data[field])
            
            user.save()
            
            # 注意：用户资料由信号自动创建，不需要手动创建
            # 创建用户资料
            # from .models import UserProfile
            # UserProfile.objects.create(user=user)
            
            logger.info(f"用户创建成功: {user.username}")
            return user
            
        except ValidationError as e:
            logger.error(f"用户创建失败 - 验证错误: {e}")
            raise
        except Exception as e:
            logger.error(f"用户创建失败: {e}")
            raise ValidationError(f"用户创建失败: {str(e)}")
    
    @staticmethod
    @transaction.atomic
    def update_user(user: User, update_data: Dict[str, Any]) -> User:
        """
        更新用户信息
        
        Args:
            user: 要更新的用户实例
            update_data: 更新数据字典
            
        Returns:
            User: 更新后的用户实例
            
        Raises:
            ValidationError: 当数据验证失败时抛出
        """
        try:
            # 更新用户字段
            update_fields = []
            
            # 基本字段
            basic_fields = ['nickname', 'email', 'phone_number', 'birth_date', 'bio', 'timezone', 'language']
            for field in basic_fields:
                if field in update_data and update_data[field] is not None:
                    setattr(user, field, update_data[field])
                    update_fields.append(field)
            
            # 如果有更新，保存用户
            if update_fields:
                user.save(update_fields=update_fields)
                logger.info(f"用户更新成功: {user.username}, 更新字段: {update_fields}")
            
            return user
            
        except ValidationError as e:
            logger.error(f"用户更新失败 - 验证错误: {e}")
            raise
        except Exception as e:
            logger.error(f"用户更新失败: {e}")
            raise ValidationError(f"用户更新失败: {str(e)}")
    
    @staticmethod
    def update_password(user: User, old_password: str, new_password: str) -> bool:
        """
        更新用户密码
        
        Args:
            user: 要更新密码的用户
            old_password: 当前密码
            new_password: 新密码
            
        Returns:
            bool: 密码更新成功返回 True
            
        Raises:
            ValidationError: 当密码验证失败时抛出
        """
        try:
            # 验证旧密码
            if not user.check_password(old_password):
                raise ValidationError("当前密码不正确")
            
            # 验证新密码
            validate_password(new_password, user)
            
            # 设置新密码
            user.set_password(new_password)
            user.save(update_fields=['password'])
            
            logger.info(f"用户密码更新成功: {user.username}")
            return True
            
        except ValidationError as e:
            logger.error(f"用户密码更新失败 - 验证错误: {e}")
            raise
        except Exception as e:
            logger.error(f"用户密码更新失败: {e}")
            raise ValidationError(f"密码更新失败: {str(e)}")
    
    @staticmethod
    def soft_delete_user(user: User) -> bool:
        """
        软删除用户
        
        Args:
            user: 要删除的用户
            
        Returns:
            bool: 删除成功返回 True
        """
        try:
            user.soft_delete()
            logger.info(f"用户软删除成功: {user.username}")
            return True
        except Exception as e:
            logger.error(f"用户软删除失败: {e}")
            raise ValidationError(f"用户删除失败: {str(e)}")
    
    @staticmethod
    def restore_user(user: User) -> bool:
        """
        恢复软删除的用户
        
        Args:
            user: 要恢复的用户
            
        Returns:
            bool: 恢复成功返回 True
        """
        try:
            user.restore()
            logger.info(f"用户恢复成功: {user.username}")
            return True
        except Exception as e:
            logger.error(f"用户恢复失败: {e}")
            raise ValidationError(f"用户恢复失败: {str(e)}")
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            User: 用户实例，不存在返回 None
        """
        try:
            return User.objects.get(username=username, is_deleted=False)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱地址
            
        Returns:
            User: 用户实例，不存在返回 None
        """
        try:
            return User.objects.get(email=email, is_deleted=False)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_by_phone(phone: str) -> Optional[User]:
        """
        根据手机号获取用户
        
        Args:
            phone: 手机号
            
        Returns:
            User: 用户实例，不存在返回 None
        """
        try:
            return User.objects.get(phone_number=phone, is_deleted=False)
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def search_users(query: str, limit: int = 20) -> list:
        """
        搜索用户
        
        Args:
            query: 搜索查询字符串
            limit: 返回结果数量限制
            
        Returns:
            list: 用户列表
        """
        from django.db.models import Q
        
        return User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(nickname__icontains=query) |
            Q(phone_number__icontains=query),
            is_deleted=False
        ).order_by('-created_at')[:limit]
    
    @staticmethod
    def verify_email(user: User) -> bool:
        """
        验证用户邮箱
        
        Args:
            user: 要验证的用户
            
        Returns:
            bool: 验证成功返回 True
        """
        try:
            user.email_verified = True
            user.save(update_fields=['email_verified'])
            logger.info(f"用户邮箱验证成功: {user.username}")
            return True
        except Exception as e:
            logger.error(f"用户邮箱验证失败: {e}")
            raise ValidationError(f"邮箱验证失败: {str(e)}")
    
    @staticmethod
    def verify_phone(user: User) -> bool:
        """
        验证用户手机
        
        Args:
            user: 要验证的用户
            
        Returns:
            bool: 验证成功返回 True
        """
        try:
            user.phone_verified = True
            user.save(update_fields=['phone_verified'])
            logger.info(f"用户手机验证成功: {user.username}")
            return True
        except Exception as e:
            logger.error(f"用户手机验证失败: {e}")
            raise ValidationError(f"手机验证失败: {str(e)}")


class UserProfileService:
    """
    用户资料服务类
    
    提供用户资料相关的业务逻辑处理方法。
    """
    
    @staticmethod
    def update_profile(user, profile_data: Dict[str, Any]):
        """
        更新用户资料
        
        Args:
            user: 用户实例
            profile_data: 资料更新数据
            
        Returns:
            UserProfile: 更新后的用户资料
        """
        try:
            # 获取或创建用户资料
            from .models import UserProfile
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user)
            
            # 更新资料字段
            update_fields = []
            profile_fields = ['gender', 'occupation', 'company', 'address', 'website', 'interests', 'social_links', 'tags', 'privacy_settings']
            
            for field in profile_fields:
                if field in profile_data and profile_data[field] is not None:
                    setattr(profile, field, profile_data[field])
                    update_fields.append(field)
            
            if update_fields:
                profile.save(update_fields=update_fields)
                logger.info(f"用户资料更新成功: {user.username}, 更新字段: {update_fields}")
            
            return profile
            
        except Exception as e:
            logger.error(f"用户资料更新失败: {e}")
            raise ValidationError(f"用户资料更新失败: {str(e)}")
    
    @staticmethod
    def get_profile(user):
        """
        获取用户资料
        
        Args:
            user: 用户实例
            
        Returns:
            UserProfile: 用户资料，不存在则创建
        """
        from .models import UserProfile
        
        try:
            return user.profile
        except UserProfile.DoesNotExist:
            return UserProfile.objects.create(user=user)