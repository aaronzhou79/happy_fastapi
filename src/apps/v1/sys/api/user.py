# src/apps/v1/sys/api/user.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : user.py
# @Software: Cursor
# @Description: 用户管理API
from src.apps.v1.sys.models.user import User, UserCreateWithRoles, UserGetWithRoles, UserUpdate
from src.apps.v1.sys.service.svr_user import svr_user
from src.common.base_api import BaseAPI

user_api = BaseAPI(
    model=User,
    service=svr_user,
    create_schema=UserCreateWithRoles,
    update_schema=UserUpdate,
    base_schema=UserGetWithRoles,
    prefix="/user",
    gen_delete=True,
    tags=["用户管理"],
)
