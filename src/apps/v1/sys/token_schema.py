#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Any

from src.apps.v1.sys.models import UserSchemaBase
from src.common.data_model.base_schema import BaseSchema


class GetSwaggerToken(BaseSchema):
    """
    获取 Swagger Token
    """
    access_token: str
    token_type: str = 'Bearer'
    user: UserSchemaBase  # type: ignore


class AccessTokenBase(BaseSchema):
    """
    访问令牌基础类
    """
    access_token: str
    access_token_type: str = 'Bearer'
    access_token_expire_time: datetime


class GetNewToken(AccessTokenBase):
    """
    获取新令牌
    """
    pass


class GetLoginToken(AccessTokenBase):
    """
    获取登录令牌
    """
    user: dict[str, Any]
