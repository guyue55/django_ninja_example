"""
用户 API 端点

提供用户管理相关的 API 接口，包括用户注册、登录、信息更新等功能。
"""

from ninja import Router
from ninja import Query
from ninja.pagination import paginate
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.exceptions import ValidationError
from typing import List, Optional
import logging

# 导入认证类
from apps.api.api import AuthBearer

# 导入服务
from .services import UserService, UserProfileService

# 导入模式
from .schemas import (
    UserCreate, UserUpdate, UserResponse, UserListResponse,
    UserPasswordUpdate, UserDetailResponse, UserFilter,
    UserProfileUpdate, UserProfileResponse
)

# 获取用户模型
User = get_user_model()

# 创建路由实例
router = Router()

# 配置日志
logger = logging.getLogger(__name__)


@router.post("/register", response=UserResponse, auth=None)
def register_user(request, user_data: UserCreate):
    """
    用户注册
    
    创建新用户账户。
    
    Args:
        request: Django 请求对象
        user_data: 用户注册数据
        
    Returns:
        UserResponse: 新创建的用户信息
        
    Raises:
        ValidationError: 当数据验证失败时抛出
    """
    try:
        # 创建用户
        user = UserService.create_user(user_data.dict())
        return user
    except ValidationError as e:
        logger.error(f"用户注册失败: {e}")
        # 返回422验证错误响应
        from django.http import JsonResponse
        return JsonResponse(
            {"detail": list(e.messages) if hasattr(e, 'messages') else [str(e)]},
            status=422
        )
    except Exception as e:
        logger.error(f"用户注册失败: {e}")
        raise


@router.get("/me", response=UserDetailResponse, auth=AuthBearer())
def get_current_user(request):
    """
    获取当前用户信息
    
    获取当前认证用户的详细信息和资料。
    
    Args:
        request: Django 请求对象
        
    Returns:
        UserDetailResponse: 当前用户的详细信息
    """
    # 获取当前用户（通过认证中间件）
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        raise ValidationError("用户未认证")
    
    try:
        user = User.objects.get(id=user_id, is_deleted=False)
        profile = UserProfileService.get_profile(user)
        
        return UserDetailResponse(
            user=user,
            profile=profile
        )
    except User.DoesNotExist:
        raise ValidationError("用户不存在")


@router.put("/me", response=UserResponse, auth=AuthBearer())
def update_current_user(request, user_data: UserUpdate):
    """
    更新当前用户信息
    
    更新当前认证用户的基本信息。
    
    Args:
        request: Django 请求对象
        user_data: 用户更新数据
        
    Returns:
        UserResponse: 更新后的用户信息
    """
    # 获取当前用户
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        raise ValidationError("用户未认证")
    
    try:
        user = User.objects.get(id=user_id, is_deleted=False)
        updated_user = UserService.update_user(user, user_data.dict(exclude_unset=True))
        return updated_user
    except User.DoesNotExist:
        raise ValidationError("用户不存在")
    except ValidationError as e:
        logger.error(f"用户信息更新失败: {e}")
        raise


@router.put("/me/password", response=dict, auth=AuthBearer())
def update_current_user_password(request, password_data: UserPasswordUpdate):
    """
    更新当前用户密码
    
    更新当前认证用户的登录密码。
    
    Args:
        request: Django 请求对象
        password_data: 密码更新数据
        
    Returns:
        dict: 操作结果消息
    """
    # 获取当前用户
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        raise ValidationError("用户未认证")
    
    try:
        user = User.objects.get(id=user_id, is_deleted=False)
        success = UserService.update_password(
            user, 
            password_data.old_password,
            password_data.new_password
        )
        
        if success:
            return {"message": "密码更新成功"}
        else:
            raise ValidationError("密码更新失败")
            
    except User.DoesNotExist:
        raise ValidationError("用户不存在")
    except ValidationError as e:
        logger.error(f"密码更新失败: {e}")
        raise


@router.get("/me/profile", response=UserProfileResponse, auth=AuthBearer())
def get_current_user_profile(request):
    """
    获取当前用户资料
    
    获取当前认证用户的详细资料信息。
    
    Args:
        request: Django 请求对象
        
    Returns:
        UserProfileResponse: 用户资料信息
    """
    # 获取当前用户
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        raise ValidationError("用户未认证")
    
    try:
        user = User.objects.get(id=user_id, is_deleted=False)
        profile = UserProfileService.get_profile(user)
        return profile
    except User.DoesNotExist:
        raise ValidationError("用户不存在")


@router.put("/me/profile", response=UserProfileResponse, auth=AuthBearer())
def update_current_user_profile(request, profile_data: UserProfileUpdate):
    """
    更新当前用户资料
    
    更新当前认证用户的详细资料信息。
    
    Args:
        request: Django 请求对象
        profile_data: 用户资料更新数据
        
    Returns:
        UserProfileResponse: 更新后的用户资料
    """
    # 获取当前用户
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        raise ValidationError("用户未认证")
    
    try:
        user = User.objects.get(id=user_id, is_deleted=False)
        profile = UserProfileService.update_profile(user, profile_data.dict(exclude_unset=True))
        return profile
    except User.DoesNotExist:
        raise ValidationError("用户不存在")
    except ValidationError as e:
        logger.error(f"用户资料更新失败: {e}")
        raise


@router.delete("/me", response=dict, auth=AuthBearer())
def delete_current_user(request):
    """
    删除当前用户（软删除）
    
    软删除当前认证用户账户。
    
    Args:
        request: Django 请求对象
        
    Returns:
        dict: 操作结果消息
    """
    # 获取当前用户
    user_id = getattr(request, 'user_id', None)
    if not user_id:
        raise ValidationError("用户未认证")
    
    try:
        user = User.objects.get(id=user_id, is_deleted=False)
        success = UserService.soft_delete_user(user)
        
        if success:
            return {"message": "账户删除成功"}
        else:
            raise ValidationError("账户删除失败")
            
    except User.DoesNotExist:
        raise ValidationError("用户不存在")


# 管理员接口（需要特殊权限）
@router.get("/", response=List[UserResponse])
@paginate  # 分页支持
def list_users(request, filters: UserFilter = Query(...)):
    """
    获取用户列表（管理员功能）
    
    获取系统用户列表，支持过滤和分页。
    
    Args:
        request: Django 请求对象
        filters: 用户过滤条件
        
    Returns:
        List[UserResponse]: 用户列表响应
    """
    # 这里应该添加管理员权限检查
    # if not request.user.is_staff:
    #     raise ValidationError("权限不足")
    
    # 构建查询
    queryset = User.objects.filter(is_deleted=False)
    
    # 应用过滤条件
    if filters.username:
        queryset = queryset.filter(username__icontains=filters.username)
    
    if filters.email:
        queryset = queryset.filter(email__icontains=filters.email)
    
    if filters.nickname:
        queryset = queryset.filter(nickname__icontains=filters.nickname)
    
    if filters.user_type:
        queryset = queryset.filter(user_type=filters.user_type)
    
    if filters.status:
        queryset = queryset.filter(status=filters.status)
    
    if filters.email_verified is not None:
        queryset = queryset.filter(email_verified=filters.email_verified)
    
    if filters.phone_verified is not None:
        queryset = queryset.filter(phone_verified=filters.phone_verified)
    
    if filters.created_at_start:
        queryset = queryset.filter(created_at__gte=filters.created_at_start)
    
    if filters.created_at_end:
        queryset = queryset.filter(created_at__lte=filters.created_at_end)
    
    # 排序
    queryset = queryset.order_by('-created_at')
    
    # 获取总数
    total = queryset.count()
    
    # 这里应该返回分页后的数据
    # 为了简化，这里返回所有数据
    users = list(queryset)
    
    return UserListResponse(
        items=users,
        total=total,
        page=1,  # 应该根据实际分页参数设置
        page_size=len(users),
        total_pages=1  # 应该根据实际分页计算
    )


@router.get("/{user_id}", response=UserDetailResponse)
def get_user_detail(request, user_id: int):
    """
    获取用户详情（管理员功能）
    
    获取指定用户的详细信息。
    
    Args:
        request: Django 请求对象
        user_id: 用户ID
        
    Returns:
        UserDetailResponse: 用户详细信息
    """
    # 这里应该添加管理员权限检查
    
    try:
        user = User.objects.get(id=user_id, is_deleted=False)
        profile = UserProfileService.get_profile(user)
        
        return UserDetailResponse(
            user=user,
            profile=profile
        )
    except User.DoesNotExist:
        raise ValidationError("用户不存在")


@router.put("/{user_id}", response=UserResponse)
def update_user(request, user_id: int, user_data: UserUpdate):
    """
    更新用户信息（管理员功能）
    
    更新指定用户的信息。
    
    Args:
        request: Django 请求对象
        user_id: 用户ID
        user_data: 用户更新数据
        
    Returns:
        UserResponse: 更新后的用户信息
    """
    # 这里应该添加管理员权限检查
    
    try:
        user = User.objects.get(id=user_id, is_deleted=False)
        updated_user = UserService.update_user(user, user_data.dict(exclude_unset=True))
        return updated_user
    except User.DoesNotExist:
        raise ValidationError("用户不存在")
    except ValidationError as e:
        logger.error(f"用户信息更新失败: {e}")
        raise


@router.delete("/{user_id}", response=dict)
def delete_user(request, user_id: int):
    """
    删除用户（管理员功能）
    
    软删除指定用户。
    
    Args:
        request: Django 请求对象
        user_id: 用户ID
        
    Returns:
        dict: 操作结果消息
    """
    # 这里应该添加管理员权限检查
    
    try:
        user = User.objects.get(id=user_id, is_deleted=False)
        success = UserService.soft_delete_user(user)
        
        if success:
            return {"message": "用户删除成功"}
        else:
            raise ValidationError("用户删除失败")
            
    except User.DoesNotExist:
        raise ValidationError("用户不存在")