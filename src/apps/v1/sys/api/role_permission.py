# src/apps/v1/sys/api/role_permission.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : role_permission.py
# @Software: Cursor
# @Description: 角色权限管理API
from src.apps.v1.sys.models.role_permission import RolePermission, RolePermissionCreate, RolePermissionUpdate
from src.apps.v1.sys.service.role_permission import svr_role_permission
from src.common.base_api import BaseAPI

role_permission_api = BaseAPI(
    module_name="sys",
    model=RolePermission,
    service=svr_role_permission,
    create_schema=RolePermissionCreate,
    update_schema=RolePermissionUpdate,
    base_schema=RolePermission,
    prefix="/role_permission",
    tags=["系统管理/角色权限管理"],
)
