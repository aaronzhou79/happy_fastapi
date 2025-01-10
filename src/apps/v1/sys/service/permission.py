# src/apps/v1/sys/service/permission.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : permission.py
# @Software: Cursor
# @Description: 部门服务


from src.apps.v1.sys.crud.permission import crud_permission
from src.common.tree_service import TreeService


class SvrPermission(TreeService):
    """
    权限服务
    """
    def __init__(self):
        super().__init__(crud=crud_permission)


svr_permission = SvrPermission()
