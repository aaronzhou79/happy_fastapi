# src/middleware/jwt_auth_middleware.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : jwt_auth_middleware.py
# @Software: Cursor
# @Description: JWT 认证中间件

from typing import Any

from fastapi import Request, Response
from fastapi.security.utils import get_authorization_scheme_param
from starlette.authentication import AuthCredentials, AuthenticationBackend, AuthenticationError, BaseUser
from starlette.requests import HTTPConnection

from src.apps.v1.sys.crud.user import crud_user
from src.apps.v1.sys.models.role import Role
from src.apps.v1.sys.models.user import UserGetWithRoles
from src.common.logger import log
from src.core.conf import settings
from src.core.exceptions.errors import TokenError
from src.core.responses.response_schema import MsgSpecJSONResponse
from src.core.security import auth_security
from src.database.db_redis import redis_client
from src.database.db_session import async_audit_session, async_session


class _AuthenticationError(AuthenticationError):
    """重写内部认证错误类"""

    def __init__(
            self,
            *,
            code: int | None = None,
            msg: str | None = None,
            headers: dict[str, Any] | None = None,
    ):
        self.code = code
        self.msg = msg
        self.headers = headers


class AuthenticatedUser(BaseUser):
    """认证用户"""

    def __init__(self, user_data: UserGetWithRoles):
        self.user_data: UserGetWithRoles = user_data

    @property
    def is_authenticated(self) -> bool:
        """是否已认证"""
        return True

    @property
    def display_name(self) -> str:
        """显示名称"""
        return str(getattr(self.user_data, 'username', ''))

    @property
    def identity(self) -> str:
        """标识"""
        return str(getattr(self.user_data, 'id', ''))


class JwtAuthMiddleware(AuthenticationBackend):
    """JWT 认证中间件"""

    @staticmethod
    def auth_exception_handler(conn: HTTPConnection, exc: _AuthenticationError) -> Response:
        """覆盖内部认证错误处理"""
        return MsgSpecJSONResponse(
            content={'code': exc.code, 'msg': exc.msg, 'data': None},
            status_code=exc.code or 401,
        )

    async def authenticate(self, request: Request) -> tuple[AuthCredentials, AuthenticatedUser] | None:
        """认证"""
        token = request.headers.get('Authorization')
        if not token:
            return None

        if request.url.path in settings.TOKEN_REQUEST_PATH_EXCLUDE:
            return None

        scheme, token = get_authorization_scheme_param(token)
        if scheme.lower() != 'bearer':
            return None

        try:
            sub = await auth_security.jwt_authentication(token)
            cache_user = await redis_client.get(f'{settings.JWT_USER_REDIS_PREFIX}:{sub}')
            if not cache_user:
                async with async_audit_session(async_session(), request=request) as db:
                    current_user = await crud_user.get_by_id(db, id=sub)
                    if current_user:
                        user_dict = await current_user.to_api_dict()
                        # 确保关系对象也被正确转换
                        if 'roles' in user_dict:
                            user_dict['roles'] = [
                                Role.model_validate(role) for role in user_dict['roles']
                            ]
                        user = UserGetWithRoles.model_validate(user_dict)
                        await redis_client.setex(
                            f'{settings.JWT_USER_REDIS_PREFIX}:{sub}',
                            settings.JWT_USER_REDIS_EXPIRE_SECONDS or 60 * 60 * 24 * 30,
                            user.model_dump_json(),
                        )
            else:
                user = UserGetWithRoles.model_validate_json(cache_user)
        except TokenError as exc:
            raise _AuthenticationError(code=exc.code, msg=exc.detail, headers=exc.headers) from exc
        except Exception as e:
            log.exception(e)
            code = getattr(e, 'code', 500)
            msg = getattr(e, 'msg', getattr(e, 'message', 'Internal Server Error'))
            if type(code) == str:  # noqa: E721
                code = 500
            raise _AuthenticationError(code=code, msg=msg) from e

        return AuthCredentials(['authenticated']), AuthenticatedUser(user)
