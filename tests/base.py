"""
API 测试基类

提供 API 测试的基础功能和辅助方法。
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json

# 获取用户模型
User = get_user_model()


class APITestCase(TestCase):
    """API 测试基类"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'nickname': '测试用户'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.token = None
    
    def login(self, username=None, password=None):
        """
        用户登录并获取访问令牌
        
        Args:
            username: 用户名，默认使用测试用户
            password: 密码，默认使用测试用户密码
            
        Returns:
            str: 访问令牌
        """
        if username is None:
            username = self.user_data['username']
        if password is None:
            password = self.user_data['password']
        
        response = self.client.post(
            '/api/auth/login',
            data={
                'username': username,
                'password': password
            },
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = json.loads(response.content)
            self.token = data.get('access_token')
            return self.token
        
        return None
    
    def auth_request(self, method, path, data=None, **kwargs):
        """
        发送需要认证的请求
        
        Args:
            method: 请求方法（'get', 'post', 'put', 'delete'）
            path: 请求路径
            data: 请求数据
            kwargs: 其他参数
            
        Returns:
            Response: Django 响应对象
        """
        if not self.token:
            self.login()
        
        # 设置认证头
        kwargs['HTTP_AUTHORIZATION'] = f'Bearer {self.token}'
        
        method_func = getattr(self.client, method.lower())
        return method_func(path, data, **kwargs)
    
    def assert_response_success(self, response, status_code=200):
        """
        断言响应成功
        
        Args:
            response: Django 响应对象
            status_code: 期望的状态码
        """
        self.assertEqual(response.status_code, status_code)
        
        try:
            data = json.loads(response.content)
            self.assertIn('success', data)
            self.assertTrue(data['success'])
        except (json.JSONDecodeError, KeyError):
            pass  # 不是所有响应都有 success 字段
    
    def assert_response_error(self, response, status_code=400):
        """
        断言响应错误
        
        Args:
            response: Django 响应对象
            status_code: 期望的状态码
        """
        self.assertEqual(response.status_code, status_code)
        
        try:
            data = json.loads(response.content)
            self.assertIn('error', data)
        except (json.JSONDecodeError, KeyError):
            pass  # 不是所有错误响应都有 error 字段
    
    def get_response_data(self, response):
        """
        获取响应数据
        
        Args:
            response: Django 响应对象
            
        Returns:
            dict: 响应数据
        """
        return json.loads(response.content)
    
    def create_test_user(self, **kwargs):
        """
        创建测试用户
        
        Args:
            kwargs: 用户数据
            
        Returns:
            User: 创建的用户实例
        """
        user_data = self.user_data.copy()
        user_data.update(kwargs)
        
        # 确保用户名和邮箱唯一
        if 'username' not in kwargs:
            user_data['username'] = f"testuser_{generate_random_string(6)}"
        if 'email' not in kwargs:
            user_data['email'] = f"test_{generate_random_string(6)}@example.com"
        
        return User.objects.create_user(**user_data)


def generate_random_string(length: int = 8) -> str:
    """
    生成随机字符串
    
    Args:
        length: 字符串长度
        
    Returns:
        str: 随机字符串
    """
    import random
    import string
    
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))