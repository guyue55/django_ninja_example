"""
Django 认证应用配置

定义认证应用的配置信息。
"""

from django.apps import AppConfig


class AuthConfig(AppConfig):
    """认证应用配置类"""
    
    # 应用名称
    name = 'apps.authentication'
    
    # 应用标签
    label = 'authentication'
    
    # 应用描述
    verbose_name = '认证授权'
    
    def ready(self):
        """
        应用就绪时的初始化操作
        
        当 Django 启动时会调用此方法，可以在这里进行信号注册等操作。
        """
        # 导入信号处理器
        from . import signals