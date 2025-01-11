# src/apps/v1/sys/crud/permission.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/01/10
# @Author  : Aaron Zhou
# @File    : permission.py
# @Software: Cursor
# @Description: 权限相关CRUD类
from src.apps.v1.sys.models.role_permission import RolePermission, RolePermissionCreate, RolePermissionUpdate
from src.common.base_crud import CRUDBase


class CrudRolePermission(CRUDBase):
    """权限相关CRUD类"""
    def __init__(self):
        super().__init__(
            model=RolePermission,
            create_model=RolePermissionCreate,
            update_model=RolePermissionUpdate,
        )


crud_role_permission = CrudRolePermission()
