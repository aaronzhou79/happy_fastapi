# src/apps/v1/sys/service/user_role.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/01/10
# @Author  : Aaron Zhou
# @File    : user_role.py
# @Software: Cursor
# @Description: 用户角色服务
from src.apps.v1.sys.crud.user_role import crud_user_role
from src.apps.v1.sys.models.user_role import UserRole, UserRoleCreate, UserRoleUpdate
from src.common.base_service import BaseService


class SvrUserRole(BaseService[UserRole, UserRoleCreate, UserRoleUpdate]):
    """
    用户角色服务
    """
    def __init__(self):
        self.crud = crud_user_role


svr_user_role = SvrUserRole()
