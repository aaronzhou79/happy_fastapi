# src/apps/v1/sys/crud/role.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : role.py
# @Software: Cursor
# @Description: 角色相关CRUD类


from src.apps.v1.sys.models.role import Role, RoleCreate, RoleUpdate
from src.common.base_crud import CRUDBase


class CrudRole(CRUDBase):
    """角色相关CRUD类"""
    def __init__(self):
        super().__init__(
            model=Role,
            create_model=RoleCreate,
            update_model=RoleUpdate,
        )


crud_role = CrudRole()
