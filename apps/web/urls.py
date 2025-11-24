"""
Web应用URL配置
遵循Google Python Style Guide
"""

from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    # 首页
    path('', views.home_view, name='home'),
    
    # 认证相关页面
    path('login/', views.login_view, name='login'),
    path('register/', views.login_view, name='register'),  # 暂时使用登录页面作为注册页面
    path('logout/', views.logout_view, name='logout'),     # 退出登录
    
    # 用户相关页面（需要登录）
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.profile_view, name='settings'),  # 暂时使用个人资料页面作为设置页面
    
    # 其他页面
    path('password-reset/', views.login_view, name='password_reset'),  # 暂时使用登录页面作为密码重置页面
]