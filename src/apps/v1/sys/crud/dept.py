# src/apps/v1/sys/crud/dept.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : dept.py
# @Software: Cursor
# @Description: 部门相关CRUD类
from src.apps.v1.sys.models.dept import Dept, DeptCreate, DeptUpdate
from src.common.base_crud import CRUDBase


class CrudDept(CRUDBase):
    """部门相关CRUD类"""


crud_dept = CrudDept(Dept, DeptCreate, DeptUpdate)
