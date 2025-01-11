# src/apps/v1/sys/service/role_permission.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : svr_role_permission.py
# @Software: Cursor
# @Description: 角色权限服务


from src.apps.v1.sys.crud.role_permission import crud_role_permission
from src.apps.v1.sys.models.role_permission import RolePermission, RolePermissionCreate, RolePermissionUpdate
from src.common.base_service import BaseService


class SvrRolePermission(BaseService[RolePermission, RolePermissionCreate, RolePermissionUpdate]):
    """
    角色权限服务
    """
    def __init__(self):
        self.crud = crud_role_permission


svr_role_permission = SvrRolePermission()
