#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import dataclasses

from datetime import datetime

from fastapi import Response

from src.common.enums import OperaLogStatusType


@dataclasses.dataclass
class IpInfo:
    """IP 信息"""
    ip: str
    country: str | None
    region: str | None
    city: str | None


@dataclasses.dataclass
class UserAgentInfo:
    """用户代理信息"""
    user_agent: str | None
    os: str | None
    browser: str | None
    device: str | None


@dataclasses.dataclass
class RequestCallNext:
    """请求调用下一个中间件"""
    code: int
    msg: str
    status: OperaLogStatusType
    err: Exception | None
    response: Response


@dataclasses.dataclass
class NewToken:
    """新令牌"""
    new_access_token: str
    new_access_token_expire_time: datetime
    new_refresh_token: str
    new_refresh_token_expire_time: datetime


@dataclasses.dataclass
class AccessToken:
    """访问令牌"""
    access_token: str
    access_token_expire_time: datetime


@dataclasses.dataclass
class RefreshToken:
    """刷新令牌"""
    refresh_token: str
    refresh_token_expire_time: datetime