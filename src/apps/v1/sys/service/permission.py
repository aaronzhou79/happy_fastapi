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
from sqlalchemy import select

from src.apps.v1.sys.crud.permission import crud_permission
from src.apps.v1.sys.models.permission import Permission, PermissionCreate
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


svr_permission = SvrPermission()
