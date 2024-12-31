# src/apps/v1/sys/api/user.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : user.py
# @Software: Cursor
# @Description: 用户管理API


from src.common.base_api import BaseAPI

from ..model.users import User, UserCreate, UserUpdate

user_api = BaseAPI(
    model=User,
    create_schema=UserCreate,
    update_schema=UserUpdate,
    prefix="/user",
    gen_delete=True,
    tags=["用户管理"],
)
