# src/apps/v1/sys/service/svr_role.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : svr_role.py
# @Software: Cursor
# @Description: 角色服务


from src.apps.v1.sys.crud.role import crud_role
from src.apps.v1.sys.models.role import Role, RoleCreate, RoleUpdate
from src.common.base_service import BaseService


class SvrRole(BaseService[Role, RoleCreate, RoleUpdate]):
    """
    角色服务
    """


svr_role = SvrRole(crud=crud_role)
