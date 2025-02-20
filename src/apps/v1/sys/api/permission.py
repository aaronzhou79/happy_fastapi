# src/apps/v1/sys/api/permission.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : permission.py
# @Software: Cursor
# @Description: 权限管理API
from fastapi import Request

from src.apps.v1.sys.models.permission import Permission, PermissionCreate, PermissionUpdate
from src.apps.v1.sys.service.permission import svr_permission
from src.common.tree_api import TreeAPI
from src.core.responses.response_schema import ResponseModel, response_base
from src.database.db_session import async_audit_session, async_session

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


@permission_api.router.post("/init")
async def init_permission(request: Request) -> ResponseModel:
    """初始化权限数据"""
    async with async_audit_session(async_session(), request) as session:
        await svr_permission.init_permission(session, request.app)
    return response_base.success(data={"message": "权限数据初始化成功"})


@permission_api.router.get("/init_menu")
async def init_menu(request: Request) -> ResponseModel:
    """初始化菜单数据"""
    async with async_audit_session(async_session(), request) as session:
        await svr_permission.init_menu(session, request.app)
    return response_base.success(data={"message": "菜单数据初始化成功"})
