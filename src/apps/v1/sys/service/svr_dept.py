# src/apps/v1/sys/service/svr_dept.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : svr_dept.py
# @Software: Cursor
# @Description: 部门服务


from src.apps.v1.sys.crud.dept import crud_dept
from src.apps.v1.sys.models.dept import Dept, DeptCreate, DeptUpdate
from src.common.base_service import BaseService


class SvrDept(BaseService[Dept, DeptCreate, DeptUpdate]):
    """
    部门服务
    """


svr_dept = SvrDept(crud=crud_dept)