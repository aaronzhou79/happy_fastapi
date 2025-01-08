#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import timedelta

from fastapi import Depends, Request
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from src.common.dataclasses import AccessToken, NewToken, RefreshToken
from src.core.conf import settings
from src.database.db_redis import redis_client
from src.utils.timezone import TimeZone

from ..exceptions.errors import AuthorizationError, TokenError

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


# JWT authorizes dependency injection
DependsJwtAuth = Depends(HTTPBearer())


def get_hash_password(password: str) -> str:
    """
    Encrypt passwords using the hash algorithm

    :param password:
    :return:
    """
    return pwd_context.hash(password)


def password_verify(plain_password: str, hashed_password: str) -> bool:
    """
    Password verification

    :param plain_password: The password to verify
    :param hashed_password: The hash ciphers to compare
    :return:
    """
    return pwd_context.verify(plain_password, hashed_password)


async def create_access_token(sub: str, multi_login: bool) -> AccessToken:
    """
    Generate encryption token

    :param sub: The subject/userid of the JWT
    :param multi_login: multipoint login for user
    :return:
    """
    expire = TimeZone.now() + timedelta(seconds=settings.TOKEN_EXPIRE_SECONDS)
    expire_seconds = settings.TOKEN_EXPIRE_SECONDS

    to_encode = {'exp': expire, 'sub': sub}
    access_token = jwt.encode(to_encode, settings.TOKEN_SECRET_KEY, settings.TOKEN_ALGORITHM)

    if multi_login is False:
        key_prefix = f'{settings.TOKEN_REDIS_PREFIX}:{sub}'
        await redis_client.delete_prefix(key_prefix)

    key = f'{settings.TOKEN_REDIS_PREFIX}:{sub}:{access_token}'
    await redis_client.setex(key, expire_seconds, access_token)
    return AccessToken(access_token=access_token, access_token_expire_time=expire)


async def create_refresh_token(sub: str, multi_login: bool) -> RefreshToken:
    """
    生成加密刷新令牌，仅用于创建新令牌

    :param sub: The subject/userid of the JWT
    :param multi_login: multipoint login for user
    :return:
    """
    expire = TimeZone.now() + timedelta(seconds=settings.TOKEN_REFRESH_EXPIRE_SECONDS)
    expire_seconds = settings.TOKEN_REFRESH_EXPIRE_SECONDS

    to_encode = {'exp': expire, 'sub': sub}
    refresh_token = jwt.encode(to_encode, settings.TOKEN_SECRET_KEY, settings.TOKEN_ALGORITHM)

    if multi_login is False:
        key_prefix = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{sub}'
        await redis_client.delete_prefix(key_prefix)

    key = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{sub}:{refresh_token}'
    await redis_client.setex(key, expire_seconds, refresh_token)
    return RefreshToken(refresh_token=refresh_token, refresh_token_expire_time=expire)


async def create_new_token(sub: str, token: str, refresh_token: str, multi_login: bool) -> NewToken:
    """
    生成新令牌

    :param sub:
    :param token
    :param refresh_token:
    :param multi_login:
    :return:
    """
    redis_refresh_token = await redis_client.get(f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{sub}:{refresh_token}')
    if not redis_refresh_token or redis_refresh_token != refresh_token:
        raise TokenError(msg='Refresh Token 已过期')

    new_access_token = await create_access_token(sub, multi_login)
    new_refresh_token = await create_refresh_token(sub, multi_login)

    token_key = f'{settings.TOKEN_REDIS_PREFIX}:{sub}:{token}'
    refresh_token_key = f'{settings.TOKEN_REFRESH_REDIS_PREFIX}:{sub}:{refresh_token}'
    await redis_client.delete(token_key)
    await redis_client.delete(refresh_token_key)
    return NewToken(
        new_access_token=new_access_token.access_token,
        new_access_token_expire_time=new_access_token.access_token_expire_time,
        new_refresh_token=new_refresh_token.refresh_token,
        new_refresh_token_expire_time=new_refresh_token.refresh_token_expire_time,
    )


async def get_token(request: Request) -> str:
    """
    获取请求头中的令牌

    :return:
    """
    authorization = request.headers.get('Authorization')
    scheme, token = get_authorization_scheme_param(authorization)
    if not authorization or scheme.lower() != 'bearer':
        raise TokenError(msg='Token 无效')
    return token


def _raise_token_error(msg: str = 'Token 无效') -> None:
    raise TokenError(msg=msg)


def jwt_decode(token: str) -> int:
    """
    解码令牌

    :param token:
    :return:
    """
    try:
        payload = jwt.decode(token, settings.TOKEN_SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM])
        sub = payload.get('sub')
        if not sub:
            _raise_token_error()
        user_id = int(str(sub))
    except ExpiredSignatureError:
        _raise_token_error('Token 已过期')
    except (JWTError, Exception):
        _raise_token_error()
    return user_id


async def jwt_authentication(token: str) -> int:
    """
    JWT 认证

    :param token:
    :return:
    """
    user_id = jwt_decode(token)
    key = f'{settings.TOKEN_REDIS_PREFIX}:{user_id}:{token}'
    token_verify = await redis_client.get(key)
    if not token_verify:
        raise TokenError(msg='Token 已过期')
    return user_id


async def superuser_verify(request: Request) -> bool:
    """
    通过令牌验证当前用户权限

    :param request:
    :return:
    """
    superuser = request.user.is_superuser
    if not superuser or not request.user.is_staff:
        raise AuthorizationError
    return superuser
