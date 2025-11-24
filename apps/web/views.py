"""
Web页面视图
遵循Google Python Style Guide
"""

from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import logout as django_logout
import logging

# 配置日志记录器
logger = logging.getLogger(__name__)


def home_view(request: HttpRequest) -> HttpResponse:
    """
    首页视图
    
    Args:
        request: HTTP请求对象
        
    Returns:
        HttpResponse: 渲染后的首页响应
        
    Raises:
        Exception: 渲染模板时发生错误
    """
    try:
        context = {
            'title': 'Django Ninja Web应用',
            'user': request.user,
        }
        
        logger.info(f"用户 {request.user.username if request.user.is_authenticated else '匿名用户'} 访问首页")
        return render(request, 'home.html', context)
        
    except Exception as e:
        logger.error(f"首页视图渲染错误: {str(e)}")
        raise


def login_view(request: HttpRequest) -> HttpResponse:
    """
    登录页面视图
    
    Args:
        request: HTTP请求对象
        
    Returns:
        HttpResponse: 渲染后的登录页面响应
        
    Raises:
        Exception: 渲染模板时发生错误
    """
    try:
        # 如果用户已登录，重定向到首页
        if request.user.is_authenticated:
            return redirect('web:home')
        
        context = {
            'title': '用户登录',
        }
        
        logger.info("用户访问登录页面")
        return render(request, 'login.html', context)
        
    except Exception as e:
        logger.error(f"登录页面视图渲染错误: {str(e)}")
        raise


def logout_view(request: HttpRequest) -> HttpResponse:
    """
    退出登录视图

    Args:
        request: HTTP请求对象

    Returns:
        HttpResponse: 重定向到登录页面的响应
    """
    # 执行退出登录
    django_logout(request)
    # 重定向到登录页面
    return redirect('web:login')

@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """
    用户控制台视图（需要登录）
    
    Args:
        request: HTTP请求对象
        
    Returns:
        HttpResponse: 渲染后的控制台页面响应
        
    Raises:
        Exception: 渲染模板时发生错误
    """
    try:
        context = {
            'title': '用户控制台',
            'user': request.user,
        }
        
        logger.info(f"用户 {request.user.username} 访问控制台")
        return render(request, 'dashboard.html', context)
        
    except Exception as e:
        logger.error(f"控制台视图渲染错误: {str(e)}")
        raise


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    """
    用户个人资料视图（需要登录）
    
    Args:
        request: HTTP请求对象
        
    Returns:
        HttpResponse: 渲染后的个人资料页面响应
        
    Raises:
        Exception: 渲染模板时发生错误
    """
    try:
        context = {
            'title': '个人资料',
            'user': request.user,
        }
        
        logger.info(f"用户 {request.user.username} 访问个人资料")
        return render(request, 'profile.html', context)
        
    except Exception as e:
        logger.error(f"个人资料视图渲染错误: {str(e)}")
        raise


@require_http_methods(["GET"])
def error_404_view(request: HttpRequest, exception: Exception) -> HttpResponse:
    """
    404错误页面视图
    
    Args:
        request: HTTP请求对象
        exception: 异常对象
        
    Returns:
        HttpResponse: 404错误页面响应
    """
    context = {
        'title': '页面未找到',
        'error_code': '404',
        'error_message': '抱歉，您访问的页面不存在',
    }
    
    logger.warning(f"404错误: {request.path}")
    response = render(request, 'error.html', context)
    response.status_code = 404
    return response


@require_http_methods(["GET"])
def error_500_view(request: HttpRequest) -> HttpResponse:
    """
    500错误页面视图
    
    Args:
        request: HTTP请求对象
        
    Returns:
        HttpResponse: 500错误页面响应
    """
    context = {
        'title': '服务器错误',
        'error_code': '500',
        'error_message': '服务器内部错误，请稍后重试',
    }
    
    logger.error(f"500错误发生在路径: {request.path}")
    response = render(request, 'error.html', context)
    response.status_code = 500
    return response