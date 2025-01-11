# src/apps/v1/sys/crud/user_role.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : user_role.py
# @Software: Cursor
# @Description: 用户角色对应表相关CRUD类
from src.apps.v1.sys.models.user_role import UserRole, UserRoleCreate, UserRoleUpdate
from src.common.base_crud import CRUDBase


class CrudUserRole(CRUDBase):
    """用户角色对应表相关CRUD类"""
    def __init__(self):
        super().__init__(
            model=UserRole,
            create_model=UserRoleCreate,
            update_model=UserRoleUpdate,
        )


crud_user_role = CrudUserRole()
