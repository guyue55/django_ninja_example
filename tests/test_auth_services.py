"""
认证服务测试

测试认证相关的服务功能。
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import jwt

# 获取用户模型
User = get_user_model()

# 导入服务
from apps.authentication.services import AuthService


class AuthServiceTest(TestCase):
    """认证服务测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'nickname': '测试用户'
        }
        self.user = User.objects.create_user(**self.user_data)
    
    def test_generate_tokens_success(self):
        """测试成功生成令牌"""
        token_data = AuthService.generate_tokens(self.user)
        
        self.assertIn('access_token', token_data)
        self.assertIn('refresh_token', token_data)
        self.assertIn('token_type', token_data)
        self.assertIn('expires_in', token_data)
        self.assertIn('user_id', token_data)
        
        self.assertEqual(token_data['token_type'], 'Bearer')
        self.assertEqual(token_data['user_id'], self.user.id)
        self.assertEqual(token_data['expires_in'], settings.JWT_EXPIRATION_HOURS * 3600)
    
    def test_verify_token_success(self):
        """测试成功验证令牌"""
        # 生成令牌
        token_data = AuthService.generate_tokens(self.user)
        access_token = token_data['access_token']
        
        # 验证令牌
        user_id = AuthService.verify_token(access_token)
        
        self.assertEqual(user_id, self.user.id)
    
    def test_verify_token_invalid(self):
        """测试验证无效令牌"""
        # 测试空令牌
        user_id = AuthService.verify_token("")
        self.assertIsNone(user_id)
        
        # 测试格式错误的令牌
        user_id = AuthService.verify_token("invalid.token.here")
        self.assertIsNone(user_id)
        
        # 测试过期令牌
        expired_token = jwt.encode(
            {
                'user_id': self.user.id,
                'token_type': 'access',
                'exp': 0,  # 已过期
                'iat': 0,
            },
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        user_id = AuthService.verify_token(expired_token)
        self.assertIsNone(user_id)
    
    def test_verify_token_wrong_type(self):
        """测试验证错误类型的令牌"""
        # 生成刷新令牌（但验证时期望访问令牌）
        refresh_token = jwt.encode(
            {
                'user_id': self.user.id,
                'token_type': 'refresh',  # 错误类型
                'exp': int((timezone.now() + timedelta(hours=1)).timestamp()),
                'iat': int(timezone.now().timestamp()),
            },
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        user_id = AuthService.verify_token(refresh_token)
        self.assertIsNone(user_id)
    
    def test_verify_token_deleted_user(self):
        """测试验证已删除用户的令牌"""
        # 生成令牌
        token_data = AuthService.generate_tokens(self.user)
        access_token = token_data['access_token']
        
        # 软删除用户
        self.user.soft_delete()
        
        # 验证令牌（应该失败）
        user_id = AuthService.verify_token(access_token)
        self.assertIsNone(user_id)
    
    def test_refresh_access_token_success(self):
        """测试成功刷新访问令牌"""
        # 生成令牌
        token_data = AuthService.generate_tokens(self.user)
        refresh_token = token_data['refresh_token']
        
        # 刷新访问令牌
        new_token_data = AuthService.refresh_access_token(refresh_token)
        
        self.assertIsNotNone(new_token_data)
        self.assertIn('access_token', new_token_data)
        self.assertIn('token_type', new_token_data)
        self.assertIn('expires_in', new_token_data)
        self.assertEqual(new_token_data['token_type'], 'Bearer')
        
        # 验证新的访问令牌
        user_id = AuthService.verify_token(new_token_data['access_token'])
        self.assertEqual(user_id, self.user.id)
    
    def test_refresh_access_token_invalid(self):
        """测试刷新无效刷新令牌"""
        # 测试无效刷新令牌
        new_token_data = AuthService.refresh_access_token("invalid.refresh.token")
        self.assertIsNone(new_token_data)
    
    def test_authenticate_user_success(self):
        """测试成功认证用户"""
        # 用户名认证
        user = AuthService.authenticate_user(self.user_data['username'], self.user_data['password'])
        self.assertEqual(user, self.user)
        
        # 邮箱认证
        user = AuthService.authenticate_user(self.user_data['email'], self.user_data['password'])
        self.assertEqual(user, self.user)
        
        # 手机号认证
        self.user.phone_number = '13800138000'
        self.user.save()
        user = AuthService.authenticate_user('13800138000', self.user_data['password'])
        self.assertEqual(user, self.user)
    
    def test_authenticate_user_invalid_password(self):
        """测试认证用户时密码错误"""
        user = AuthService.authenticate_user(self.user_data['username'], 'wrongpassword')
        self.assertIsNone(user)
    
    def test_authenticate_user_invalid_username(self):
        """测试认证用户时用户名错误"""
        user = AuthService.authenticate_user('wrongusername', self.user_data['password'])
        self.assertIsNone(user)
    
    def test_authenticate_user_inactive_status(self):
        """测试认证非活跃状态用户"""
        # 修改用户状态
        self.user.status = 'inactive'
        self.user.save()
        
        user = AuthService.authenticate_user(self.user_data['username'], self.user_data['password'])
        self.assertIsNone(user)
    
    def test_logout_user_success(self):
        """测试成功登出用户"""
        # 生成令牌
        token_data = AuthService.generate_tokens(self.user)
        
        # 登出用户
        success = AuthService.logout_user(self.user.id, token_data['refresh_token'])
        
        self.assertTrue(success)
        
        # 验证刷新令牌已失效
        new_token_data = AuthService.refresh_access_token(token_data['refresh_token'])
        self.assertIsNone(new_token_data)
    
    def test_validate_token_format(self):
        """测试验证令牌格式"""
        # 有效格式
        valid_token = "header.payload.signature"
        self.assertTrue(AuthService.validate_token_format(valid_token))
        
        # 无效格式
        invalid_tokens = [
            "",
            "invalid",
            "header.payload",  # 缺少签名
            "header.payload.signature.extra",  # 多余部分
            None,
        ]
        
        for token in invalid_tokens:
            self.assertFalse(AuthService.validate_token_format(token))
    
    def test_generate_password_reset_token(self):
        """测试生成密码重置令牌"""
        reset_token = AuthService.generate_password_reset_token(self.user)
        
        self.assertIsNotNone(reset_token)
        self.assertTrue(len(reset_token) > 0)
        
        # 验证重置令牌
        user = AuthService.verify_password_reset_token(reset_token)
        self.assertEqual(user, self.user)
    
    def test_verify_password_reset_token_success(self):
        """测试成功验证密码重置令牌"""
        reset_token = AuthService.generate_password_reset_token(self.user)
        
        user = AuthService.verify_password_reset_token(reset_token)
        self.assertEqual(user, self.user)
    
    def test_verify_password_reset_token_invalid(self):
        """测试验证无效密码重置令牌"""
        # 测试无效令牌
        user = AuthService.verify_password_reset_token("invalid.reset.token")
        self.assertIsNone(user)
    
    def test_reset_user_password_success(self):
        """测试成功重置用户密码"""
        # 生成重置令牌
        reset_token = AuthService.generate_password_reset_token(self.user)
        new_password = "newpassword123"
        
        # 重置密码
        success = AuthService.reset_user_password(reset_token, new_password)
        
        self.assertTrue(success)
        
        # 验证新密码
        user = AuthService.authenticate_user(self.user_data['username'], new_password)
        self.assertEqual(user, self.user)
    
    def test_reset_user_password_invalid_token(self):
        """测试使用无效令牌重置密码"""
        success = AuthService.reset_user_password("invalid.token", "newpassword123")
        self.assertFalse(success)