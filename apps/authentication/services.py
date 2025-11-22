"""
认证业务逻辑服务

包含用户认证相关的业务逻辑处理，如登录、登出、Token 管理等功能。
"""

import jwt
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.conf import settings
from django.core.exceptions import ValidationError
import logging

# 获取用户模型
User = get_user_model()

# 配置日志
logger = logging.getLogger(__name__)


class AuthService:
    """
    认证服务类
    
    提供用户认证相关的业务逻辑处理方法，包括 JWT Token 的生成、验证、刷新等。
    """
    
    # Token 类型常量
    ACCESS_TOKEN_TYPE = 'access'
    REFRESH_TOKEN_TYPE = 'refresh'
    
    @staticmethod
    def generate_tokens(user: User) -> Dict[str, str]:
        """
        生成用户认证令牌
        
        生成访问令牌和刷新令牌。
        
        Args:
            user: 用户实例
            
        Returns:
            Dict[str, str]: 包含访问令牌和刷新令牌的字典
        """
        # 生成访问令牌
        access_token = AuthService._generate_token(
            user_id=user.id,
            token_type=AuthService.ACCESS_TOKEN_TYPE,
            expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        )
        
        # 生成刷新令牌
        refresh_token = AuthService._generate_token(
            user_id=user.id,
            token_type=AuthService.REFRESH_TOKEN_TYPE,
            expires_delta=timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS)
        )
        
        # 存储刷新令牌到缓存
        cache_key = f"refresh_token:{user.id}"
        cache.set(cache_key, refresh_token, timeout=settings.JWT_REFRESH_EXPIRATION_DAYS * 24 * 3600)
        
        logger.info(f"用户令牌生成成功: {user.username}")
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': settings.JWT_EXPIRATION_HOURS * 3600,  # 转换为秒
            'user_id': user.id
        }
    
    @staticmethod
    def _generate_token(user_id: int, token_type: str, expires_delta: timedelta) -> str:
        """
        生成 JWT Token
        
        Args:
            user_id: 用户ID
            token_type: 令牌类型（access 或 refresh）
            expires_delta: 过期时间间隔
            
        Returns:
            str: JWT Token 字符串
        """
        # 当前时间
        now = datetime.utcnow()
        
        # 过期时间
        expire = now + expires_delta
        
        # Token 载荷
        payload = {
            'user_id': user_id,
            'token_type': token_type,
            'exp': int(expire.timestamp()),
            'iat': int(now.timestamp()),  # 签发时间
            'jti': secrets.token_urlsafe(16),  # JWT ID，用于防止重放攻击
        }
        
        # 生成 Token
        token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return token
    
    @staticmethod
    def verify_token(token: str) -> Optional[int]:
        """
        验证 JWT Token
        
        验证 Token 的有效性和完整性。
        
        Args:
            token: JWT Token 字符串
            
        Returns:
            Optional[int]: 如果验证成功返回用户ID，失败返回 None
        """
        try:
            # 解码 Token
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # 验证 Token 类型
            if payload.get('token_type') != AuthService.ACCESS_TOKEN_TYPE:
                logger.warning(f"Token 类型错误: {payload.get('token_type')}")
                return None
            
            # 获取用户ID
            user_id = payload.get('user_id')
            if not user_id:
                logger.warning("Token 中缺少用户ID")
                return None
            
            # 检查用户是否存在且有效
            try:
                user = User.objects.get(id=user_id, is_deleted=False, status='active')
                return user_id
            except User.DoesNotExist:
                logger.warning(f"Token 对应的用户不存在或无效: {user_id}")
                return None
                
        except jwt.ExpiredSignatureError:
            logger.warning("Token 已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Token 验证失败: {e}")
            return None
        except Exception as e:
            logger.error(f"Token 验证异常: {e}")
            return None
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[Dict[str, str]]:
        """
        刷新访问令牌
        
        使用刷新令牌生成新的访问令牌。
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            Optional[Dict[str, str]]: 如果成功返回新的访问令牌信息，失败返回 None
        """
        try:
            # 验证刷新令牌
            payload = jwt.decode(
                refresh_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # 验证 Token 类型
            if payload.get('token_type') != AuthService.REFRESH_TOKEN_TYPE:
                logger.warning(f"刷新令牌类型错误: {payload.get('token_type')}")
                return None
            
            # 获取用户ID
            user_id = payload.get('user_id')
            if not user_id:
                logger.warning("刷新令牌中缺少用户ID")
                return None
            
            # 检查用户是否存在且有效
            try:
                user = User.objects.get(id=user_id, is_deleted=False, status='active')
            except User.DoesNotExist:
                logger.warning(f"刷新令牌对应的用户不存在: {user_id}")
                return None
            
            # 验证缓存中的刷新令牌
            cache_key = f"refresh_token:{user_id}"
            cached_token = cache.get(cache_key)
            if not cached_token or cached_token != refresh_token:
                logger.warning(f"刷新令牌无效或已过期: {user_id}")
                return None
            
            # 生成新的访问令牌
            new_access_token = AuthService._generate_token(
                user_id=user_id,
                token_type=AuthService.ACCESS_TOKEN_TYPE,
                expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS)
            )
            
            logger.info(f"访问令牌刷新成功: {user.username}")
            
            return {
                'access_token': new_access_token,
                'token_type': 'Bearer',
                'expires_in': settings.JWT_EXPIRATION_HOURS * 3600
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("刷新令牌已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"刷新令牌验证失败: {e}")
            return None
        except Exception as e:
            logger.error(f"刷新访问令牌异常: {e}")
            return None
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        """
        用户认证
        
        验证用户身份。
        
        Args:
            username: 用户名、邮箱或手机号
            password: 密码
            
        Returns:
            Optional[User]: 如果认证成功返回用户实例，失败返回 None
        """
        # 尝试不同的登录方式
        user = None
        
        # 1. 用户名登录
        user = authenticate(username=username, password=password)
        
        # 2. 邮箱登录
        if not user:
            try:
                user_obj = User.objects.get(email=username, is_deleted=False)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        # 3. 手机号登录
        if not user:
            try:
                user_obj = User.objects.get(phone_number=username, is_deleted=False)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        # 检查用户状态
        if user and user.status != 'active':
            logger.warning(f"用户账户状态异常: {username} - {user.status}")
            return None
        
        if user:
            logger.info(f"用户认证成功: {username}")
        else:
            logger.warning(f"用户认证失败: {username}")
        
        return user
    
    @staticmethod
    def logout_user(user_id: int, refresh_token: Optional[str] = None) -> bool:
        """
        用户登出
        
        清除用户的认证状态和令牌。
        
        Args:
            user_id: 用户ID
            refresh_token: 刷新令牌（可选）
            
        Returns:
            bool: 登出成功返回 True
        """
        try:
            # 清除缓存中的刷新令牌
            cache_key = f"refresh_token:{user_id}"
            cache.delete(cache_key)
            
            # 如果提供了刷新令牌，也可以将其加入黑名单
            if refresh_token:
                try:
                    payload = jwt.decode(
                        refresh_token,
                        settings.JWT_SECRET_KEY,
                        algorithms=[settings.JWT_ALGORITHM]
                    )
                    jti = payload.get('jti')
                    if jti:
                        # 将 Token ID 加入黑名单
                        blacklist_key = f"blacklist_token:{jti}"
                        expire_time = payload.get('exp', 0) - int(datetime.utcnow().timestamp())
                        if expire_time > 0:
                            cache.set(blacklist_key, True, timeout=expire_time)
                except Exception:
                    pass  # 忽略刷新令牌处理错误
            
            logger.info(f"用户登出成功: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"用户登出失败: {e}")
            return False
    
    @staticmethod
    def validate_token_format(token: str) -> bool:
        """
        验证 Token 格式
        
        检查 Token 字符串是否符合 JWT 格式要求。
        
        Args:
            token: Token 字符串
            
        Returns:
            bool: 格式正确返回 True
        """
        if not token or not isinstance(token, str):
            return False
        
        # JWT Token 应该包含两个点号
        parts = token.split('.')
        if len(parts) != 3:
            return False
        
        return True
    
    @staticmethod
    def generate_password_reset_token(user: User) -> str:
        """
        生成密码重置令牌
        
        生成用于密码重置的安全令牌。
        
        Args:
            user: 用户实例
            
        Returns:
            str: 密码重置令牌
        """
        # 生成重置令牌（使用 JWT）
        reset_token = AuthService._generate_token(
            user_id=user.id,
            token_type='reset',
            expires_delta=timedelta(hours=12)  # 12小时过期 (JWT最小要求)
        )
        
        # 存储重置令牌到缓存
        cache_key = f"password_reset:{user.id}"
        cache.set(cache_key, reset_token, timeout=12 * 3600)  # 12小时过期
        
        logger.info(f"密码重置令牌生成成功: {user.username}")
        return reset_token
    
    @staticmethod
    def verify_password_reset_token(token: str) -> Optional[User]:
        """
        验证密码重置令牌
        
        验证密码重置令牌的有效性。
        
        Args:
            token: 密码重置令牌
            
        Returns:
            Optional[User]: 如果验证成功返回用户实例，失败返回 None
        """
        try:
            # 验证令牌
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # 验证 Token 类型
            if payload.get('token_type') != 'reset':
                logger.warning(f"重置令牌类型错误: {payload.get('token_type')}")
                return None
            
            # 获取用户ID
            user_id = payload.get('user_id')
            if not user_id:
                logger.warning("重置令牌中缺少用户ID")
                return None
            
            # 检查用户是否存在
            try:
                user = User.objects.get(id=user_id, is_deleted=False)
                return user
            except User.DoesNotExist:
                logger.warning(f"重置令牌对应的用户不存在: {user_id}")
                return None
                
        except jwt.ExpiredSignatureError:
            logger.warning("重置令牌已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"重置令牌验证失败: {e}")
            return None
        except Exception as e:
            logger.error(f"重置令牌验证异常: {e}")
            return None
    
    @staticmethod
    def reset_user_password(token: str, new_password: str) -> bool:
        """
        重置用户密码
        
        使用有效的重置令牌重置用户密码。
        
        Args:
            token: 密码重置令牌
            new_password: 新密码
            
        Returns:
            bool: 重置成功返回 True
        """
        try:
            # 验证重置令牌
            user = AuthService.verify_password_reset_token(token)
            if not user:
                return False
            
            # 更新密码
            user.set_password(new_password)
            user.save(update_fields=['password'])
            
            # 清除重置令牌
            cache_key = f"password_reset:{user.id}"
            cache.delete(cache_key)
            
            logger.info(f"用户密码重置成功: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"用户密码重置失败: {e}")
            return False