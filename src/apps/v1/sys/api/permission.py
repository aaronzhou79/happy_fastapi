# src/apps/v1/sys/api/permission.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : permission.py
# @Software: Cursor
# @Description: 权限管理API
from src.apps.v1.sys.models.permission import Permission, PermissionCreate, PermissionUpdate
from src.apps.v1.sys.service.permission import svr_permission
from src.common.tree_api import TreeAPI

# 创建部门API路由
permission_api = TreeAPI(
    module_name="sys",
    model=Permission,
    service=svr_permission,
    create_schema=PermissionCreate,
    update_schema=PermissionUpdate,
    base_schema=Permission,
    prefix="/permission",
    gen_delete=True,
    tags=["系统管理/权限管理"]
)

# 获取路由器
router = permission_api.router
