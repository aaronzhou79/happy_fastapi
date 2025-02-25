# src/apps/v1/sys/service/permission.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : permission.py
# @Software: Cursor
# @Description: 部门服务

import re

from typing import Sequence

from fastapi import FastAPI
from sqlalchemy import Column, select

from src.apps.v1.sys.crud.crud_permission import crud_permission
from src.apps.v1.sys.models.mdl_permission import Permission, PermissionCreate
from src.common.enums import PermissionType
from src.common.logger import log
from src.common.tree_service import TreeService
from src.database.db_session import AuditAsyncSession, async_session


class SvrPermission(TreeService):
    """
    权限服务
    """
    def __init__(self):
        self.tree_crud = self.crud = crud_permission
        self.model = Permission

    async def get_role_permissions(
        self,
        session: AuditAsyncSession,
        role_id: list[int] | int
    ) -> Sequence[Permission]:
        """
        获取角色权限
        """
        if isinstance(role_id, int):
            role_ids = [role_id]
        else:
            role_ids = role_id
        return await self.crud.get_permissions_by_role(session, role_ids)

    async def init_permission(self, session: AuditAsyncSession, app: FastAPI) -> None:
        """初始化权限数据"""
        try:
            # 获取所有路由
            routes = app.router.routes

            # 生成权限规则
            perms = []
            for route in routes:
                if hasattr(route, "dependencies"):
                    # 解析路由权限依赖
                    for dep in route.dependencies:  # type: ignore
                        if hasattr(dep, "dependency") and hasattr(dep.dependency, 'permissions'):
                            perms.append(
                                PermissionCreate(
                                    name=route.tags[0] or route.name,  # type: ignore
                                    code=re.sub(r'/api/v\d+/', '', route.path).replace("/", "_"),  # type: ignore
                                    type=PermissionType.API,
                                    api_path=route.path,  # type: ignore
                                    api_method=route.methods.pop(),  # type: ignore
                                    perm_code=",".join(dep.dependency.permissions)
                                )
                            )

            # 写入数据库
            # 查询现有规则
            stmt = select(Permission)
            result = await session.execute(stmt)
            exists = {(r.code, r.api_method): r for r in result.scalars()}

            # 更新或插入规则
            for perm in perms:
                key = (perm.code, perm.api_method)
                if key not in exists:
                    await self.crud.create(session, obj_in=perm)

            await session.commit()

            log.info("🟢 权限规则初始化成功")
        except Exception as e:
            log.error("❌ 权限规则初始化失败: {}", str(e))

    async def init_menu(self, session: AuditAsyncSession, app: FastAPI) -> None:
        """初始化菜单数据"""
        menus = [
            {
                "name": "系统管理",
                "code": "sys_manage",
                "notes": "系统管理",
                "type": PermissionType.MENU,
                "parent_id": None,
                "children": [
                    {
                        "name": "权限管理",
                        "code": "sys_permission",
                        "notes": "权限管理",
                        "type": PermissionType.MENU,
                        "route_path": "/sys/permission",
                        "route_component": "sys/permission/index",
                        "route_title": "权限管理",
                        "route_icon": "icon-setting",
                        "route_hidden": False,
                        "route_keep_alive": True,
                        "route_always_show": False,
                        "parent_id": None,
                    },
                    {
                        "name": "角色管理",
                        "code": "sys_role",
                        "notes": "角色管理",
                        "type": PermissionType.MENU,
                        "route_path": "/sys/role",
                        "route_component": "sys/role/index",
                        "route_title": "角色管理",
                        "route_icon": "icon-setting",
                        "route_hidden": False,
                        "route_keep_alive": True,
                        "route_always_show": False,
                        "parent_id": None,
                    },
                    {
                        "name": "用户管理",
                        "code": "sys_user",
                        "notes": "用户管理",
                        "type": PermissionType.MENU,
                        "route_path": "/sys/user",
                        "route_component": "sys/user/index",
                        "route_title": "用户管理",
                        "route_icon": "icon-setting",
                        "route_hidden": False,
                        "route_keep_alive": True,
                        "route_always_show": False,
                        "parent_id": None,
                    }
                ]
            }
        ]

        stmt = select(self.model).where(self.model.type == PermissionType.MENU)  # type: ignore
        result = await session.execute(stmt)
        exists = {(r.code): r for r in result.scalars()}

        async def create_menu(session: AuditAsyncSession, menu: dict) -> None:
            key = (menu["code"])
            if key not in exists:
                menu_obj = await self.crud.create(session, obj_in=menu)
            else:
                menu_obj = exists[key]
            if menu.get("children"):
                for child in menu["children"]:
                    child["parent_id"] = menu_obj.id
                    await create_menu(session, menu=child)

        for menu in menus:
            await create_menu(session, menu=menu)


svr_permission = SvrPermission()
