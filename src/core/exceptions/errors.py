# src/core/exceptions/errors.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any

from fastapi import HTTPException
from starlette.background import BackgroundTask

from ..responses.response_code import ResponseCode


class BaseError(Exception):
    """基础异常类"""
    code: int

    def __init__(self, *, msg: str | None = None, data: Any = None, background: BackgroundTask | None = None):
        self.msg = msg
        self.data = data
        # The original background task: https://www.starlette.io/background/
        self.background = background


class HTTPError(HTTPException):
    """处理HTTP错误的基础异常类"""
    def __init__(self, *, code: int, msg: Any = None, headers: dict[str, Any] | None = None):
        super().__init__(status_code=code, detail=msg, headers=headers)


class CustomError(BaseError):
    """处理自定义响应码的错误"""
    def __init__(self, *, error: ResponseCode, data: Any = None, background: BackgroundTask | None = None):
        self.code = error.code
        super().__init__(msg=error.msg, data=data, background=background)


class RequestError(BaseError):
    """请求参数错误"""
    code = ResponseCode.PARAMS_ERROR.code

    def __init__(self, *, msg: str = 'Bad Request', data: Any = None, background: BackgroundTask | None = None):
        super().__init__(msg=msg, data=data, background=background)


class ForbiddenError(BaseError):
    """禁止访问"""
    code = ResponseCode.FORBIDDEN.code

    def __init__(self, *, msg: str = 'Forbidden', data: Any = None, background: BackgroundTask | None = None):
        super().__init__(msg=msg, data=data, background=background)


class NotFoundError(BaseError):
    """资源未找到"""
    code = ResponseCode.NOT_FOUND.code

    def __init__(self, *, msg: str = 'Not Found', data: Any = None, background: BackgroundTask | None = None):
        super().__init__(msg=msg, data=data, background=background)


class ServerError(BaseError):
    """服务器内部错误"""
    code = ResponseCode.SERVER_ERROR.code

    def __init__(
        self, *, msg: str = 'Internal Server Error', data: Any = None, background: BackgroundTask | None = None
    ):
        super().__init__(msg=msg, data=data, background=background)


class GatewayError(BaseError):
    """网关相关的错误"""
    code = ResponseCode.GATEWAY_ERROR.code

    def __init__(self, *, msg: str = 'Bad Gateway', data: Any = None, background: BackgroundTask | None = None):
        super().__init__(msg=msg, data=data, background=background)


class AuthorizationError(BaseError):
    """授权相关的错误"""
    code = ResponseCode.UNAUTHORIZED.code

    def __init__(self, *, msg: str = 'Permission Denied', data: Any = None, background: BackgroundTask | None = None):
        super().__init__(msg=msg, data=data, background=background)


class TokenError(HTTPError):
    """令牌认证相关的错误"""
    code = ResponseCode.UNAUTHORIZED.code

    def __init__(self, *, msg: str = 'Not Authenticated', headers: dict[str, Any] | None = None):
        super().__init__(code=self.code, msg=msg, headers=headers or {'WWW-Authenticate': 'Bearer'})
