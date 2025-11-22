"""
Django 应用配置

定义 API 应用的配置信息，包括应用名称、标签等。
"""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """API 应用配置类"""
    
    # 应用名称，对应 Python 模块路径
    name = 'apps.api'
    
    # 应用标签，用于 Django 管理界面
    label = 'api'
    
    # 应用描述
    verbose_name = 'API 接口'
    
    def ready(self):
        """
        应用就绪时的初始化操作
        
        当 Django 启动时会调用此方法，可以在这里进行信号注册等初始化操作。
        """
        # 导入信号处理器（如果有的话）
        # from . import signals