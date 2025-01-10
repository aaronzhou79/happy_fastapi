# src/apps/v1/sys/api/role.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : role.py
# @Software: Cursor
# @Description: 角色管理API
from src.apps.v1.sys.models.role import Role, RoleBase, RoleCreate, RoleUpdate
from src.apps.v1.sys.service.role import svr_role
from src.common.base_api import BaseAPI

role_api = BaseAPI(
    model=Role,
    service=svr_role,
    create_schema=RoleCreate,
    update_schema=RoleUpdate,
    base_schema=RoleBase,
    prefix="/role",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=["系统管理/角色管理"],
)
