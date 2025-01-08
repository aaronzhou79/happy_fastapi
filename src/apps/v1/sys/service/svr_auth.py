#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any

from fastapi import Request, Response
from fastapi.security import HTTPBasicCredentials
from starlette.background import BackgroundTask, BackgroundTasks

from src.apps.v1.sys.crud.user import crud_user
from src.apps.v1.sys.models import AuthLoginParam, LoginLogSchemaCreate, User
from src.apps.v1.sys.service.svr_login_log import SvrLoginLog
from src.apps.v1.sys.token_schema import GetLoginToken, GetNewToken
from src.common.base_service import BaseService
from src.common.enums import LoginLogStatusType, UserStatus
from src.core.conf import settings
from src.core.exceptions import errors
from src.core.security.jwt import (
    create_access_token,
    create_new_token,
    create_refresh_token,
    get_token,
    jwt_decode,
    password_verify,
)
from src.database.db_redis import redis_client
from src.database.db_session import AuditAsyncSession, async_audit_session, async_session
from src.utils.timezone import TimeZone


class AuthService(BaseService[User, AuthLoginParam, AuthLoginParam]):
    """用户认证服务"""
    @staticmethod
    async def login(
        *, request: Request, response: Response, obj: AuthLoginParam, background_tasks: BackgroundTasks
    ) -> GetLoginToken:
        """登录"""
        def _record_login_log(
            session: AuditAsyncSession,
            request: Request,
            user_uuid: str,
            username: str | None,
            status: LoginLogStatusType,
            msg: str,
        ) -> BackgroundTask:
            return BackgroundTask(
                    SvrLoginLog.create_login_log,
                    session=session,
                    login_log_in=LoginLogSchemaCreate(
                        user_uuid=user_uuid,                  # type: ignore
                        username=username,                    # type: ignore
                        status=status,                        # type: ignore
                        ip=request.state.ip,                  # type: ignore
                        country=request.state.country,        # type: ignore
                        region=request.state.region,          # type: ignore
                        city=request.state.city,              # type: ignore
                        user_agent=request.state.user_agent,  # type: ignore
                        browser=request.state.browser,        # type: ignore
                        os=request.state.os,                  # type: ignore
                        device=request.state.device,          # type: ignore
                        login_time=TimeZone.now(),            # type: ignore
                        msg=msg,                              # type: ignore
                    ),
                )

        async with async_audit_session(async_session(), request=request) as session:
            if settings.CAPTCHA_NEED:
                captcha_code = await redis_client.get(
                    f'{settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{request.state.ip}')
                if not captcha_code:
                    raise errors.RequestError(msg='验证码失效，请重新获取')
                if captcha_code.lower() != obj.captcha.lower():
                    raise errors.RequestError(msg='验证码有误')
            current_user = await crud_user.get_by_fields(session=session, username=obj.username)
            if current_user is None:
                raise errors.RequestError(msg="用户名有误!")
            user_uuid = current_user.uuid
            username = current_user.username
            if not password_verify(f'{obj.password}{current_user.salt}', f'{current_user.password}'):
                task = _record_login_log(
                    session, request, user_uuid, username, LoginLogStatusType.fail, '用户名或密码有误')
                raise errors.AuthorizationError(msg='用户名或密码有误', background=task)

            if not current_user.status and current_user.status != UserStatus.ACTIVE:
                task = _record_login_log(
                    session, request, user_uuid, username, LoginLogStatusType.fail, '用户已被锁定, 请联系统管理员')
                raise errors.AuthorizationError(msg='用户已被锁定, 请联系统管理员', background=task)

            current_user_id = current_user.id
            access_token = await create_access_token(str(current_user_id), current_user.is_multi_login)
            refresh_token = await create_refresh_token(str(current_user_id), current_user.is_multi_login)

            task = _record_login_log(session, request, user_uuid, username, LoginLogStatusType.success, '登录成功')
            background_tasks.add_task(task)

            if settings.CAPTCHA_NEED:
                await redis_client.delete(f'{settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{request.state.ip}')
            await crud_user.update(
                session=session,
                db_obj=current_user,
                obj_in={"last_login_time": TimeZone.now()},
            )
            try:
                response.set_cookie(
                    key=settings.COOKIE_REFRESH_TOKEN_KEY,
                    value=refresh_token.refresh_token,
                    max_age=settings.COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS,
                    expires=TimeZone.f_utc(refresh_token.refresh_token_expire_time),
                    httponly=True,
                )
            except Exception as e:
                errors.TokenError(msg=f'set cookie error: {str(e)}')
            await session.refresh(current_user)
            user_dict = await current_user.to_dict()
            return GetLoginToken(
                access_token=access_token.access_token,
                access_token_expire_time=access_token.access_token_expire_time,
                user=user_dict,
            )

    @staticmethod
    async def new_token(*, request: Request, response: Response) -> GetNewToken:
        """刷新token"""
        refresh_token = request.cookies.get(settings.COOKIE_REFRESH_TOKEN_KEY or 'fba_refresh_token')
        if not refresh_token:
            raise errors.TokenError(msg='Refresh Token 丢失，请重新登录')
        try:
            user_id = jwt_decode(refresh_token)
        except Exception as e:
            raise errors.TokenError(msg='Refresh Token 无效') from e
        if request.user.id != user_id:
            raise errors.TokenError(msg='Refresh Token 无效')
        async with async_audit_session(async_session(), None) as db:
            current_user = await crud_user.get_by_fields(session=db, id=user_id)
            if not current_user:
                raise errors.RequestError(msg='用户名或密码有误')
            if not current_user.status:
                raise errors.AuthorizationError(msg='用户已被锁定, 请联系统管理员')
            current_token = await get_token(request)
            new_token = await create_new_token(
                sub=str(current_user.id),
                token=current_token,
                refresh_token=refresh_token,
                multi_login=current_user.is_multi_login,
            )
            response.set_cookie(
                key=settings.COOKIE_REFRESH_TOKEN_KEY or 'fba_refresh_token',
                value=new_token.new_refresh_token,
                max_age=settings.COOKIE_REFRESH_TOKEN_EXPIRE_SECONDS,
                expires=TimeZone.f_utc(new_token.new_refresh_token_expire_time),
                httponly=True,
            )
            return GetNewToken(
                access_token=new_token.new_access_token,
                access_token_expire_time=new_token.new_access_token_expire_time,
            )

    @staticmethod
    async def logout(*, request: Request, response: Response) -> None:
        """登出"""
        token = await get_token(request)
        refresh_token = request.cookies.get(settings.COOKIE_REFRESH_TOKEN_KEY)
        response.delete_cookie(settings.COOKIE_REFRESH_TOKEN_KEY)
        if hasattr(request, 'user') and request.user.is_multi_login:
            key = f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}:{token}'
            await redis_client.delete(key)
            if refresh_token:
                key = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.id}:{refresh_token}'
                await redis_client.delete(key)
        else:
            key_prefix = f'{settings.TOKEN_REDIS_PREFIX}:{request.user.id}:'
            await redis_client.delete_prefix(key_prefix)
            key_prefix = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.id}:'
            await redis_client.delete_prefix(key_prefix)

    @staticmethod
    async def set_as_user(*, request: Request, id: int, username: str, password: str, roles: list[int] | None = None) -> None:
        """设置为用户"""
        async with async_audit_session(async_session(), request=request) as session:
            await crud_user.set_as_user(session=session, id=id, username=username, password=password, roles=roles)


