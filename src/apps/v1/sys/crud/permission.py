# src/apps/v1/sys/crud/permission.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/01/10
# @Author  : Aaron Zhou
# @File    : permission.py
# @Software: Cursor
# @Description: 权限相关CRUD类
from src.apps.v1.sys.models.permission import Permission, PermissionCreate, PermissionUpdate
from src.common.tree_crud import TreeCRUD


class CrudPermission(TreeCRUD):
    """权限相关CRUD类"""
    def __init__(self):
        super().__init__(
            model=Permission,
            create_model=PermissionCreate,
            update_model=PermissionUpdate,
        )


crud_permission = CrudPermission()
