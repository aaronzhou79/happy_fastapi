# src/apps/v1/sys/service/svr_dept.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : svr_dept.py
# @Software: Cursor
# @Description: 部门服务


from src.apps.v1.sys.crud.dept import crud_dept
from src.common.tree_service import TreeService


class SvrDept(TreeService):
    """
    部门服务
    """
    def __init__(self):
        super().__init__(crud=crud_dept)


svr_dept = SvrDept()
