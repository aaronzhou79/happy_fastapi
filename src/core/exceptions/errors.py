#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局业务异常类

业务代码执行异常时，可以使用 raise xxxError 触发内部错误，它尽可能实现带有后台任务的异常，但它不适用于**自定义响应状态码**
如果要求使用**自定义响应状态码**，则可以通过 return response_base.fail(res=CustomResponseCode.xxx) 直接返回
"""  # noqa: E501

from typing import Any

from fastapi import HTTPException
from starlette.background import BackgroundTask

from ..responses.response_code import CustomErrorCode, StandardResponseCode

ErrorData = str | dict[str, Any] | list[str] | None


class BaseError(Exception):
    """
    基础异常类
    """
    code: int

    def __init__(
        self,
        *,
        msg: str | None = None,
        data: ErrorData = None,
        background: BackgroundTask | None = None
    ):
        self.msg = msg
        self.data = data
        # The original background task: https://www.starlette.io/background/
        self.background = background


class HTTPError(HTTPException):
    """
    HTTP 异常类
    """
    def __init__(self, *, code: int, msg: Any = None, headers: dict[str, Any] | None = None):
        super().__init__(status_code=code, detail=msg, headers=headers)


class CustomError(BaseError):
    """
    自定义异常类
    """
    def __init__(self, *, error: CustomErrorCode, data: Any = None, background: BackgroundTask | None = None):
        self.code = error.code
        super().__init__(msg=error.msg, data=data, background=background)


class RequestError(BaseError):
    """
    请求错误异常类
    """
    code = StandardResponseCode.HTTP_400

    def __init__(self, *, msg: str = 'Bad Request', data: Any = None, background: BackgroundTask | None = None):
        super().__init__(msg=msg, data=data, background=background)


class ForbiddenError(BaseError):
    """
    禁止访问异常类
    """
    code = StandardResponseCode.HTTP_403

    def __init__(self, *, msg: str = 'Forbidden', data: Any = None, background: BackgroundTask | None = None):
        super().__init__(msg=msg, data=data, background=background)


class NotFoundError(BaseError):
    """
    未找到异常类
    """
    code = StandardResponseCode.HTTP_404

    def __init__(self, *, msg: str = 'Not Found', data: Any = None, background: BackgroundTask | None = None):
        super().__init__(msg=msg, data=data, background=background)


class ServerError(BaseError):
    """
    服务器错误异常类
    """
    code = StandardResponseCode.HTTP_500

    def __init__(
        self, *, msg: str = 'Internal Server Error', data: Any = None, background: BackgroundTask | None = None
    ):
        super().__init__(msg=msg, data=data, background=background)


class GatewayError(BaseError):
    """
    网关错误异常类
    """
    code = StandardResponseCode.HTTP_502

    def __init__(self, *, msg: str = 'Bad Gateway', data: Any = None, background: BackgroundTask | None = None):
        super().__init__(msg=msg, data=data, background=background)


class AuthorizationError(BaseError):
    """
    授权错误异常类
    """
    code = StandardResponseCode.HTTP_401

    def __init__(self, *, msg: str = 'Permission Denied', data: Any = None, background: BackgroundTask | None = None):
        super().__init__(msg=msg, data=data, background=background)


class TokenError(HTTPError):
    """
    令牌错误异常类
    """
    code = StandardResponseCode.HTTP_401

    def __init__(self, *, msg: str = 'Not Authenticated', headers: dict[str, Any] | None = None):
        super().__init__(code=self.code, msg=msg, headers=headers or {'WWW-Authenticate': 'Bearer'})


class RuleExecutionError(BaseError):
    """
    规则执行错误异常类
    """
    code = StandardResponseCode.HTTP_400

    def __init__(self, *, msg: str = 'Rule Execution Error', data: Any = None, background: BackgroundTask | None = None):
        super().__init__(msg=msg, data=data, background=background)


class DBError(BaseError):
    """
    数据库错误异常类
    """
    code = StandardResponseCode.HTTP_500

    def __init__(self, *, msg: str = 'Database Error', data: Any = None, background: BackgroundTask | None = None):
        super().__init__(msg=msg, data=data, background=background)
