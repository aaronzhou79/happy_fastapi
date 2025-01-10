# src/apps/v1/sys/api/dept.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : dept.py
# @Software: Cursor
# @Description: 部门管理API
from src.apps.v1.sys.models.dept import Dept, DeptCreate, DeptUpdate, DeptWithUsers
from src.apps.v1.sys.service.dept import svr_dept
from src.common.tree_api import TreeAPI

# 创建部门API路由
dept_api = TreeAPI(
    model=Dept,
    service=svr_dept,
    create_schema=DeptCreate,
    update_schema=DeptUpdate,
    base_schema=DeptWithUsers,
    prefix="/dept",
    tags=["系统管理/部门管理"]
)

# 获取路由器
router = dept_api.router
