# src/apps/v1/sys/api/dept.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : dept.py
# @Software: Cursor
# @Description: 用户管理API



from src.apps.v1.sys.models.dept import Dept, DeptBase, DeptCreate, DeptUpdate, DeptWithUsers
from src.apps.v1.sys.service.svr_dept import svr_dept
from src.common.base_api import BaseAPI

dept_api = BaseAPI(
    model=Dept,
    service=svr_dept,
    create_schema=DeptCreate,
    update_schema=DeptUpdate,
    base_schema=DeptBase,
    with_schema=DeptWithUsers,
    prefix="/dept",
    gen_delete=True,
    gen_bulk_delete=True,
    gen_bulk_create=True,
    tags=["部门管理"],
)
