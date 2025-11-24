"""
Web应用配置
遵循Google Python Style Guide
"""

from django.apps import AppConfig


class WebConfig(AppConfig):
    """
    Web应用配置类
    
    配置Django Ninja Web应用的Web界面相关设置
    """
    
    # 应用名称
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.web'
    
    # 应用标签
    label = 'web'
    
    # 应用描述
    verbose_name = 'Web界面'
    
    def ready(self):
        """
        应用准备就绪时的初始化操作
        
        当Django应用加载完成时执行，用于注册信号处理器等初始化操作
        """
        # 可以在这里添加信号处理器或其他初始化代码
        pass