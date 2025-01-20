# src/apps/v1/sys/crud/permission.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/01/10
# @Author  : Aaron Zhou
# @File    : permission.py
# @Software: Cursor
# @Description: 权限相关CRUD类
from typing import Sequence

from sqlmodel import select

from src.apps.v1.sys.models.permission import Permission, PermissionCreate, PermissionUpdate
from src.apps.v1.sys.models.role_permission import RolePermission
from src.apps.v1.sys.models.user_role import UserRole
from src.common.tree_crud import TreeCRUD
from src.database.db_session import AuditAsyncSession


class CrudPermission(TreeCRUD):
    """权限相关CRUD类"""
    def __init__(self) -> None:
        super().__init__(Permission, PermissionCreate, PermissionUpdate)

    async def get_permissions_by_role(
        self,
        session: AuditAsyncSession,
        role_ids: list[int]
    ) -> Sequence[Permission]:
        """
        获取角色权限
        """
        stmt = (
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id.in_(role_ids))  # type: ignore
        )
        result = await session.execute(stmt)
        data = result.scalars().all()
        return await self.to_tree_dict(data)

    async def get_permissions_by_user(
        self,
        session: AuditAsyncSession,
        user_id: int,
        is_superuser: bool
    ) -> Sequence[Permission]:
        """获取用户权限"""
        if is_superuser:
            data = await self.get_multi(session=session, limit=10000)
        else:
            stmt = (
                select(Permission)
                .join(RolePermission, RolePermission.permission_id == Permission.id)
                .join(UserRole, UserRole.role_id == RolePermission.role_id)   # type: ignore
                .where(UserRole.user_id == user_id)
            )
            result = await session.execute(stmt)
            data = result.scalars().all()
        return await self.to_tree_dict(data)


crud_permission = CrudPermission()
