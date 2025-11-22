"""
通用工具函数

提供项目中常用的工具函数和辅助方法。
"""

import re
import uuid
import random
import string
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def generate_random_string(length: int = 8, charset: str = None) -> str:
    """
    生成随机字符串
    
    Args:
        length: 字符串长度
        charset: 字符集，默认为大小写字母和数字
        
    Returns:
        str: 随机字符串
    """
    if charset is None:
        charset = string.ascii_letters + string.digits
    
    return ''.join(random.choice(charset) for _ in range(length))


def generate_uuid() -> str:
    """
    生成 UUID
    
    Returns:
        str: UUID 字符串
    """
    return str(uuid.uuid4())


def generate_order_number(prefix: str = "ORD") -> str:
    """
    生成订单号
    
    Args:
        prefix: 订单号前缀
        
    Returns:
        str: 订单号
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = generate_random_string(6, string.digits)
    return f"{prefix}{timestamp}{random_part}"


def validate_phone_number(phone: str) -> bool:
    """
    验证手机号格式
    
    Args:
        phone: 手机号字符串
        
    Returns:
        bool: 格式正确返回 True
    """
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def validate_chinese_name(name: str) -> bool:
    """
    验证中文姓名格式
    
    Args:
        name: 姓名字符串
        
    Returns:
        bool: 格式正确返回 True
    """
    # 支持中英文姓名，2-20个字符
    pattern = r'^[\u4e00-\u9fa5a-zA-Z]{2,20}$'
    return bool(re.match(pattern, name))


def validate_id_card(id_card: str) -> bool:
    """
    验证身份证号格式
    
    Args:
        id_card: 身份证号字符串
        
    Returns:
        bool: 格式正确返回 True
    """
    pattern = r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$'
    return bool(re.match(pattern, id_card))


def mask_sensitive_info(info: str, mask_char: str = '*', show_chars: int = 3) -> str:
    """
    脱敏处理敏感信息
    
    Args:
        info: 敏感信息字符串
        mask_char: 掩码字符
        show_chars: 显示字符数
        
    Returns:
        str: 脱敏后的字符串
    """
    if not info:
        return ""
    
    if len(info) <= show_chars:
        return info
    
    masked_part = mask_char * (len(info) - show_chars)
    visible_part = info[-show_chars:] if show_chars > 0 else ""
    
    return masked_part + visible_part


def mask_email(email: str) -> str:
    """
    脱敏处理邮箱地址
    
    Args:
        email: 邮箱地址
        
    Returns:
        str: 脱敏后的邮箱地址
    """
    try:
        validate_email(email)
    except ValidationError:
        return mask_sensitive_info(email)
    
    username, domain = email.split('@')
    masked_username = mask_sensitive_info(username, show_chars=2)
    return f"{masked_username}@{domain}"


def mask_phone(phone: str) -> str:
    """
    脱敏处理手机号
    
    Args:
        phone: 手机号
        
    Returns:
        str: 脱敏后的手机号
    """
    if not validate_phone_number(phone):
        return mask_sensitive_info(phone)
    
    return f"{phone[:3]}****{phone[-4:]}"


def get_client_ip(request) -> str:
    """
    获取客户端真实IP地址
    
    Args:
        request: Django 请求对象
        
    Returns:
        str: 客户端IP地址
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def is_ajax_request(request) -> bool:
    """
    判断是否为 AJAX 请求
    
    Args:
        request: Django 请求对象
        
    Returns:
        bool: 是 AJAX 请求返回 True
    """
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def get_user_agent_info(request) -> Dict[str, str]:
    """
    获取用户代理信息
    
    Args:
        request: Django 请求对象
        
    Returns:
        Dict[str, str]: 用户代理信息
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    info = {
        'user_agent': user_agent,
        'is_mobile': 'Mobile' in user_agent,
        'is_tablet': 'Tablet' in user_agent,
        'is_wechat': 'MicroMessenger' in user_agent,
        'is_qq': 'QQ' in user_agent,
    }
    
    # 浏览器信息
    if 'Chrome' in user_agent:
        info['browser'] = 'Chrome'
    elif 'Firefox' in user_agent:
        info['browser'] = 'Firefox'
    elif 'Safari' in user_agent and 'Chrome' not in user_agent:
        info['browser'] = 'Safari'
    elif 'Edge' in user_agent:
        info['browser'] = 'Edge'
    elif 'Trident' in user_agent or 'MSIE' in user_agent:
        info['browser'] = 'IE'
    else:
        info['browser'] = 'Unknown'
    
    return info


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        str: 格式化后的文件大小
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """
    截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 后缀字符串
        
    Returns:
        str: 截断后的文本
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def clean_html_tags(html_text: str) -> str:
    """
    清除HTML标签
    
    Args:
        html_text: 包含HTML标签的文本
        
    Returns:
        str: 清除标签后的纯文本
    """
    import re
    
    # 清除HTML标签
    clean_text = re.sub(r'<[^>]+>', '', html_text)
    
    # 清除HTML实体
    clean_text = re.sub(r'&[a-zA-Z]+;', '', clean_text)
    clean_text = re.sub(r'&#[0-9]+;', '', clean_text)
    
    return clean_text.strip()


def is_valid_json(json_string: str) -> bool:
    """
    验证JSON字符串格式
    
    Args:
        json_string: JSON字符串
        
    Returns:
        bool: 格式正确返回 True
    """
    import json
    
    try:
        json.loads(json_string)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def safe_int(value: Any, default: int = 0) -> int:
    """
    安全转换为整数
    
    Args:
        value: 要转换的值
        default: 转换失败时的默认值
        
    Returns:
        int: 转换后的整数
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    安全转换为浮点数
    
    Args:
        value: 要转换的值
        default: 转换失败时的默认值
        
    Returns:
        float: 转换后的浮点数
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def get_time_ago(dt: datetime) -> str:
    """
    获取相对时间描述
    
    Args:
        dt: 时间对象
        
    Returns:
        str: 相对时间描述（如：5分钟前）
    """
    now = timezone.now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years}年前"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months}个月前"
    elif diff.days > 0:
        return f"{diff.days}天前"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}小时前"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}分钟前"
    else:
        return "刚刚"


def batch_process(items: List[Any], batch_size: int = 100) -> List[List[Any]]:
    """
    批量处理列表
    
    Args:
        items: 要处理的列表
        batch_size: 每批大小
        
    Returns:
        List[List[Any]]: 分批后的列表
    """
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]


def remove_duplicate_preserve_order(items: List[Any]) -> List[Any]:
    """
    去重并保持顺序
    
    Args:
        items: 要去重的列表
        
    Returns:
        List[Any]: 去重后的列表
    """
    seen = set()
    result = []
    
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    
    return result