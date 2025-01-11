#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import Request, Response
from starlette.background import BackgroundTask, BackgroundTasks

from src.apps.v1.sys.crud.user import crud_user
from src.apps.v1.sys.models.login_log import LoginLogCreate
from src.apps.v1.sys.models.user import (
    AuthLoginParam,
    GetLoginToken,
    GetNewToken,
    User,
    UserCreate,
    UserGetWithRoles,
    UserUpdate,
)
from src.apps.v1.sys.service.login_log import svr_login_log
from src.common.base_service import BaseService
from src.common.enums import LoginLogStatus, UserStatus
from src.core.conf import settings
from src.core.exceptions import errors
from src.core.security.jwt import (
    create_access_token,
    create_new_token,
    create_refresh_token,
    get_token,
    jwt_decode,
)
from src.database.db_redis import redis_client
from src.database.db_session import AuditAsyncSession, async_audit_session, async_session
from src.utils.encrypt import verify_password
from src.utils.timezone import TimeZone
from src.utils.trace_id import get_request_trace_id


class AuthService(BaseService[User, UserCreate, UserUpdate]):
    """用户认证服务"""
    def __init__(self):
        self.crud = crud_user
    @staticmethod
    async def get_user_by_id(*, id: int) -> User | None:
        """根据用户ID获取用户"""
        async with async_session() as session:
            user = await crud_user.get_by_fields(session=session, id=id)
            if len(user) != 1:
                return None
            return user[0]

    """用户认证服务"""
    async def login(
        self,
        *,
        request: Request,
        response: Response,
        obj: AuthLoginParam,
        background_tasks: BackgroundTasks
    ) -> GetLoginToken:
        """登录"""
        def _record_login_log(
            session: AuditAsyncSession,
            request: Request,
            user_uuid: str,
            username: str | None,
            status: LoginLogStatus,
            msg: str,
        ) -> BackgroundTask:
            return BackgroundTask(
                svr_login_log.create_login_log(
                    session=session,
                    login_log_in=LoginLogCreate(
                        trace_id=get_request_trace_id(request),  # type: ignore
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
            )

        # 检查登录失败次数
        fail_count_key = f"login:fail_count:{request.state.ip}"
        fail_count = await redis_client.get(fail_count_key)
        if fail_count and int(fail_count) >= 5:
            raise errors.RequestError(data="登录失败次数过多,请15分钟后重试")

        async with async_audit_session(async_session(), request=request) as session:
            if settings.CAPTCHA_NEED:
                captcha_code = await redis_client.get(
                    f'{settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{request.state.ip}')
                if not captcha_code:
                    raise errors.RequestError(data='验证码失效，请重新获取')
                if captcha_code.lower() != obj.captcha.lower():
                    raise errors.RequestError(data='验证码有误')
            current_user = await crud_user.get_by_fields(session=session, username=obj.username)
            if len(current_user) != 1:
                await self._handle_login_fail(request.state.ip)
                raise errors.RequestError(data="用户名或密码错误")
            current_user = current_user[0]
            user_uuid = current_user.uuid
            username = current_user.username
            if not verify_password(str(obj.password), str(current_user.salt), str(current_user.password)):
                await self._handle_login_fail(request.state.ip)
                raise errors.RequestError(data="用户名或密码错误")

            if not current_user.status and current_user.status != UserStatus.ACTIVE:
                task = _record_login_log(
                    session, request, user_uuid, username, LoginLogStatus.FAIL, '用户已被锁定, 请联系统管理员')
                raise errors.AuthorizationError(msg='用户已被锁定, 请联系统管理员', background=task)

            current_user_id = current_user.id
            access_token = await create_access_token(str(current_user_id), current_user.is_multi_login)
            refresh_token = await create_refresh_token(str(current_user_id), current_user.is_multi_login)

            task = _record_login_log(session, request, user_uuid, username, LoginLogStatus.SUCCESS, '登录成功')
            background_tasks.add_task(task)

            if settings.CAPTCHA_NEED:
                await redis_client.delete(f'{settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{request.state.ip}')
            await crud_user.update(
                session=session,
                obj_in={"id": current_user_id, "last_login_time": TimeZone.now()},
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
            user_dict = await current_user.to_dict(max_depth=1)
            return GetLoginToken(
                access_token=access_token.access_token,
                access_token_expire_time=access_token.access_token_expire_time,
                user=UserGetWithRoles.model_validate(user_dict),
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
            if len(current_user) != 1:
                raise errors.RequestError(data='用户名或密码有误')
            current_user = current_user[0]
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
        if hasattr(request, 'user') and request.user.user_data.is_multi_login:
            key = f'{settings.TOKEN_REDIS_PREFIX}:{request.user.user_data.id}:{token}'
            await redis_client.delete(key)
            if refresh_token:
                key = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.user_data.id}:{refresh_token}'
                await redis_client.delete(key)
        else:
            key_prefix = f'{settings.TOKEN_REDIS_PREFIX}:{request.user.user_data.id}:'
            await redis_client.delete_prefix(key_prefix)
            key_prefix = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{request.user.user_data.id}:'
            await redis_client.delete_prefix(key_prefix)

    @staticmethod
    async def set_as_user(*, request: Request, id: int, username: str, password: str, roles: list[int] | None = None) -> None:
        """设置为用户"""
        async with async_audit_session(async_session(), request=request) as session:
            await crud_user.set_as_user(session=session, id=id, username=username, password=password, roles=roles)

    async def _handle_login_fail(self, ip: str) -> None:
        """处理登录失败"""
        key = f"login:fail_count:{ip}"
        fail_count = await redis_client.get(key)
        if fail_count:
            fail_count = int(fail_count) + 1
            await redis_client.setex(key, 900, fail_count)  # 15分钟后过期
        else:
            await redis_client.setex(key, 900, 1)


svr_auth = AuthService()
