"""
健康检查路由

提供系统健康状态检查接口，用于监控系统运行状态。
"""

from ninja import Router
from ninja import Schema
from django.db import connection
from django.core.cache import cache
from datetime import datetime
import logging

# 创建路由实例
router = Router()

# 配置日志
logger = logging.getLogger(__name__)


class HealthResponse(Schema):
    """健康检查响应模式"""
    status: str  # 系统状态
    timestamp: str  # 检查时间戳
    database: str  # 数据库状态
    cache: str  # 缓存状态
    uptime: str  # 系统运行时间


class HealthDetailResponse(Schema):
    """详细健康检查响应模式"""
    status: str
    timestamp: str
    checks: dict  # 各项检查详情


@router.get("/", response=HealthResponse)
def health_check(request):
    """
    基础健康检查
    
    检查系统的基本运行状态，包括数据库和缓存连接。
    
    Returns:
        HealthResponse: 包含系统状态信息的响应
    """
    timestamp = datetime.now().isoformat()
    
    # 检查数据库连接
    db_status = "healthy"
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception as e:
        db_status = "unhealthy"
        logger.error(f"数据库连接检查失败: {e}")
    
    # 检查缓存连接
    cache_status = "healthy"
    try:
        cache.set("health_check", timestamp, timeout=5)
        cached_value = cache.get("health_check")
        if cached_value != timestamp:
            cache_status = "unhealthy"
    except Exception as e:
        cache_status = "unhealthy"
        logger.error(f"缓存连接检查失败: {e}")
    
    # 确定整体状态
    overall_status = "healthy" if db_status == "healthy" and cache_status == "healthy" else "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        timestamp=timestamp,
        database=db_status,
        cache=cache_status,
        uptime="running"  # 可以扩展为实际的运行时间计算
    )


@router.get("/detailed", response=HealthDetailResponse)
def health_check_detailed(request):
    """
    详细健康检查
    
    提供系统各组件的详细状态信息。
    
    Returns:
        HealthDetailResponse: 包含详细检查信息的响应
    """
    timestamp = datetime.now().isoformat()
    checks = {}
    
    # 数据库详细检查
    db_checks = {}
    try:
        with connection.cursor() as cursor:
            # 检查连接
            cursor.execute("SELECT 1")
            cursor.fetchone()
            db_checks["connection"] = "healthy"
            
            # 检查响应时间
            import time
            start_time = time.time()
            cursor.execute("SELECT COUNT(*) FROM pg_stat_activity")  # PostgreSQL 特定查询
            cursor.fetchone()
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒
            db_checks["response_time_ms"] = round(response_time, 2)
            
            # 检查连接数（PostgreSQL）
            cursor.execute("SELECT count(*) FROM pg_stat_activity")
            connection_count = cursor.fetchone()[0]
            db_checks["active_connections"] = connection_count
            
    except Exception as e:
        db_checks["connection"] = "unhealthy"
        db_checks["error"] = str(e)
        logger.error(f"数据库详细检查失败: {e}")
    
    checks["database"] = db_checks
    
    # 缓存详细检查
    cache_checks = {}
    try:
        # 基本连接测试
        test_key = "health_check_detailed"
        test_value = timestamp
        cache.set(test_key, test_value, timeout=10)
        cached_value = cache.get(test_key)
        
        if cached_value == test_value:
            cache_checks["connection"] = "healthy"
            cache_checks["read_write"] = "healthy"
        else:
            cache_checks["connection"] = "unhealthy"
            cache_checks["read_write"] = "unhealthy"
            
        # 检查缓存统计信息（如果可用）
        try:
            cache_stats = cache._cache.get_stats()  # Redis 特定
            if cache_stats:
                cache_checks["stats"] = cache_stats
        except AttributeError:
            pass  # 不是 Redis 缓存，忽略统计信息
            
    except Exception as e:
        cache_checks["connection"] = "unhealthy"
        cache_checks["error"] = str(e)
        logger.error(f"缓存详细检查失败: {e}")
    
    checks["cache"] = cache_checks
    
    # 系统资源检查
    system_checks = {}
    try:
        import psutil
        
        # CPU 使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        system_checks["cpu_percent"] = cpu_percent
        system_checks["cpu_status"] = "healthy" if cpu_percent < 80 else "warning"
        
        # 内存使用率
        memory = psutil.virtual_memory()
        system_checks["memory_percent"] = memory.percent
        system_checks["memory_status"] = "healthy" if memory.percent < 80 else "warning"
        system_checks["memory_available_gb"] = round(memory.available / (1024**3), 2)
        
        # 磁盘使用率
        disk = psutil.disk_usage('/')
        system_checks["disk_percent"] = disk.percent
        system_checks["disk_status"] = "healthy" if disk.percent < 80 else "warning"
        system_checks["disk_free_gb"] = round(disk.free / (1024**3), 2)
        
    except ImportError:
        system_checks["psutil"] = "not_available"
    except Exception as e:
        system_checks["error"] = str(e)
        logger.error(f"系统资源检查失败: {e}")
    
    checks["system"] = system_checks
    
    # 确定整体状态
    overall_status = "healthy"
    for component, status_data in checks.items():
        if isinstance(status_data, dict):
            if status_data.get("connection") == "unhealthy":
                overall_status = "unhealthy"
                break
            elif status_data.get("status") == "warning":
                overall_status = "warning"
    
    return HealthDetailResponse(
        status=overall_status,
        timestamp=timestamp,
        checks=checks
    )