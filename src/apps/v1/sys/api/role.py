# src/apps/v1/sys/api/role.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : role.py
# @Software: Cursor
# @Description: 角色管理API
from src.common.base_api import BaseAPI

from ..models import Role, RoleSchemaBase, RoleSchemaCreate, RoleSchemaUpdate

role_api = BaseAPI(
    model=Role,
    create_schema=RoleSchemaCreate,
    update_schema=RoleSchemaUpdate,
    base_schema=RoleSchemaBase,
    prefix="/role",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=["角色管理"],
)
