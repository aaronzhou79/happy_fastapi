# src/apps/v1/sys/api/user_role.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/01/10
# @Author  : Aaron Zhou
# @File    : user_role.py
# @Software: Cursor
# @Description: 用户角色管理API
from src.apps.v1.sys.models.user_role import UserRole, UserRoleBase, UserRoleCreate, UserRoleUpdate
from src.apps.v1.sys.service.user_role import svr_user_role
from src.common.base_api import BaseAPI

user_role_api = BaseAPI(
    model=UserRole,
    service=svr_user_role,
    create_schema=UserRoleCreate,
    update_schema=UserRoleUpdate,
    base_schema=UserRoleBase,
    prefix="/user_role",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=["系统管理/用户角色管理"],
)
