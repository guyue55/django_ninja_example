"""Django-Ninja API 的响应工具与带标签的整型枚举。

提供功能：
- `IntEnumChoices`：在 `IntEnum` 基础上为每个成员绑定人类可读的 `label`，行为与
  Django 的 `models.IntegerChoices` 类似。
- `BusinessCode`：统一的业务码枚举。
- `HttpStatus`：常见的 HTTP 状态码枚举。
- `ApiResponse`：统一构建成功/失败/异常/分页等响应的辅助方法。

示例：
    >>> BusinessCode.OK.label
    '操作成功'
    >>> BusinessCode.get_label(100401)
    '未认证'
    >>> BusinessCode.choices()[:2]
    [(0, '操作成功'), (100100, '操作失败')]
    >>> payload, status = ApiResponse.created({'id': 1})
    >>> int(status)
    201
"""

from enum import IntEnum
from typing import Tuple


class IntEnumChoices(IntEnum):
    """为枚举成员增加 `label` 标签的整型枚举。

    每个枚举成员以 `(value, label)` 的形式定义，成员既可当作整型使用，又携带
    人类可读的标签。该行为与 Django 的 `IntegerChoices` 在非模型场景下类似。
    """
    def __new__(cls, value, label):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj

    @classmethod
    def get_label(cls, value: int, default=None) -> str:
        """根据枚举整型值返回对应成员的标签。

        Args:
            value: 要查询的枚举整型值。
            default: 查找失败时返回的默认标签。

        Returns:
            指定值对应的标签；如果不存在该成员，则返回 `default`。
        """
        try:
            return cls(value).label
        except Exception:
            return default

    @classmethod
    def choices(cls):
        """返回所有成员的 `(value, label)` 列表。

        与 Django 字段的 `choices` 用法保持一致，便于在模型或序列化附近复用。
        """
        return [(member.value, member.label) for member in cls]


class BusinessCode(IntEnumChoices):
    """统一的业务结果码，成员为整型值并携带人类可读标签。

    常用方式：
        - 按名称访问：`BusinessCode.OK`
        - 按值访问：`BusinessCode(100401)`
        - 获取标签：`BusinessCode.OK.label` 或 `BusinessCode.get_label(0)`
        - 获取选项：`BusinessCode.choices()`（返回 `(value, label)` 列表）
    """
    OK = 0, "操作成功"
    GENERIC_ERROR = 100100, "操作失败"
    BAD_REQUEST = 100400, "请求错误"
    UNAUTHORIZED = 100401, "未认证"
    FORBIDDEN = 100403, "无权限"
    NOT_FOUND = 100404, "资源不存在"
    CONFLICT = 100409, "资源冲突"
    UNPROCESSABLE_ENTITY = 100422, "参数验证失败"
    INTERNAL_ERROR = 100500, "服务器内部错误"


class HttpStatus(IntEnumChoices):
    """常见的 HTTP 状态码及其标签。"""
    OK = 200, "OK"
    CREATED = 201, "Created"
    BAD_REQUEST = 400, "Bad Request"
    UNAUTHORIZED = 401, "Unauthorized"
    FORBIDDEN = 403, "Forbidden"
    NOT_FOUND = 404, "Not Found"
    CONFLICT = 409, "Conflict"
    UNPROCESSABLE_ENTITY = 422, "Unprocessable Entity"
    INTERNAL_ERROR = 500, "Internal Server Error"


class ApiResponse:
    """构建统一的 API 响应载荷和返回状态的辅助方法。

    所有方法返回包含标准键的 Python 字典，并在需要时返回对应的 `HttpStatus`
    作为 HTTP 状态码。
    """
    @staticmethod
    def success(data=None, message: str = None, code: int = 0, meta: dict=None):
        """构建成功响应载荷。

        Args:
            data: 响应数据。
            message: 响应消息；默认使用 `code` 对应的标签。
            code: 业务码；默认使用 `BusinessCode.OK` 的值。
            meta: 额外元信息（如分页元数据）。

        Returns:
            包含 `code`、`message`、`data` 及可选 `meta` 的字典。
        """
        msg = message or BusinessCode.get_label(code)
        if meta:
            meta["code"] = code
            meta["message"] = msg
            meta["data"] = data

        return {"code": code, "message": msg, "data": data}

    @staticmethod
    def created(data=None, message: str = None) -> Tuple[dict, int]:
        """构建 201 Created 响应。

        Args:
            data: 新建资源的表示数据。
            message: 响应消息；默认 "创建成功"。

        Returns:
            `(payload, HttpStatus.CREATED)` 元组。
        """
        msg = message or "创建成功"
        return ApiResponse.success(data=data, message=msg), HttpStatus.CREATED

    @staticmethod
    def error(message: str = None, code: int = BusinessCode.GENERIC_ERROR, data=None, errors=None):
        """构建不包含 HTTP 状态码的错误载荷。

        Args:
            message: 错误消息；默认使用 `code` 对应的标签。
            code: 业务码；默认 `BusinessCode.GENERIC_ERROR`。
            data: 额外上下文数据。
            errors: 验证错误或字段错误。

        Returns:
            错误载荷字典。
        """
        msg = message or BusinessCode.get_label(code)
        payload = {"code": code, "message": msg, "data": data}
        if errors is not None:
            payload["errors"] = errors
        return payload

    @staticmethod
    def fail(message: str = None, code: int = BusinessCode.BAD_REQUEST, status: int = HttpStatus.BAD_REQUEST, data=None, errors=None) -> Tuple[dict, int]:
        """构建 400 Bad Request 响应。

        Args:
            message: 失败消息；默认使用 `code` 或 `status` 对应的标签。
            code: 业务码；默认 `BusinessCode.BAD_REQUEST`。
            status: HTTP 状态码；默认 `HttpStatus.BAD_REQUEST`。
            data: 额外上下文数据。
            errors: 验证或字段错误。

        Returns:
            `(payload, status)` 元组，包含失败详情。
        """
        msg = message or BusinessCode.get_label(code) or HttpStatus.get_label(status)
        return ApiResponse.error(message=msg, code=code, data=data, errors=errors), status

    @staticmethod
    def not_found(message: str = None, code: int = BusinessCode.NOT_FOUND) -> Tuple[dict, int]:
        """构建 404 Not Found 响应。

        Args:
            message: 响应消息；默认使用 `code` 对应的标签。
            code: 业务码；默认 `BusinessCode.NOT_FOUND`。

        Returns:
            `(payload, HttpStatus.NOT_FOUND)` 元组。
        """
        msg = message or BusinessCode.get_label(code)
        return ApiResponse.error(message=msg, code=code), HttpStatus.NOT_FOUND

    @staticmethod
    def unauthorized(message: str = None, code: int = BusinessCode.UNAUTHORIZED) -> Tuple[dict, int]:
        """构建 401 Unauthorized 响应。"""
        msg = message or BusinessCode.get_label(code)
        return ApiResponse.error(message=msg, code=code), HttpStatus.UNAUTHORIZED

    @staticmethod
    def forbidden(message: str = None, code: int = BusinessCode.FORBIDDEN) -> Tuple[dict, int]:
        """构建 403 Forbidden 响应。"""
        msg = message or BusinessCode.get_label(code)
        return ApiResponse.error(message=msg, code=code), HttpStatus.FORBIDDEN

    @staticmethod
    def conflict(message: str = None, code: int = BusinessCode.CONFLICT) -> Tuple[dict, int]:
        """构建 409 Conflict 响应。"""
        msg = message or BusinessCode.get_label(code)
        return ApiResponse.error(message=msg, code=code), HttpStatus.CONFLICT

    @staticmethod
    def unprocessable_entity(message: str = None, errors=None, code: int = BusinessCode.UNPROCESSABLE_ENTITY) -> Tuple[dict, int]:
        """构建 422 Unprocessable Entity 响应。

        Args:
            message: 响应消息；默认使用 `code` 对应的标签。
            errors: 验证错误集合。
            code: 业务码；默认 `BusinessCode.UNPROCESSABLE_ENTITY`。

        Returns:
            `(payload, HttpStatus.UNPROCESSABLE_ENTITY)` 元组。
        """
        msg = message or BusinessCode.get_label(code)
        return ApiResponse.error(message=msg, code=code, errors=errors), HttpStatus.UNPROCESSABLE_ENTITY

    @staticmethod
    def internal_error(message: str = None, code: int = BusinessCode.INTERNAL_ERROR, data=None) -> Tuple[dict, int]:
        """构建 500 Internal Server Error 响应。"""
        msg = message or BusinessCode.get_label(code)
        return ApiResponse.error(message=msg, code=code, data=data), HttpStatus.INTERNAL_ERROR

    @staticmethod
    def code_description(code: int) -> str:
        """返回业务 `code` 整型值对应的标签。"""
        return BusinessCode.get_label(code)

    @staticmethod
    def status_description(status: int) -> str:
        """返回 HTTP `status` 整型值对应的标签。"""
        return HttpStatus.get_label(status)

    @staticmethod
    def paginate(items, total: int, page: int, page_size: int, message: str = "操作成功"):
        """构建标准的分页成功响应。

        Args:
            items: 当前页的数据列表或可迭代对象。
            total: 所有页的总数据条数。
            page: 当前页码，1 开始。
            page_size: 每页数据条数。
            message: 成功消息；默认为 "操作成功"。

        Returns:
            包含 `meta` 分页元数据的响应字典。
        """
        if page <= 0:
            page = 1
        if page_size <= 0:
            page_size = 20
        total_pages = (total + page_size - 1) // page_size
        meta = {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }
        return ApiResponse.success(data=items, message=message, code=0, meta=meta)


if __name__ == "__main__":
    print(BusinessCode.choices())
    print(HttpStatus.choices())
    print(HttpStatus.OK.label)
    print(HttpStatus.OK.value)