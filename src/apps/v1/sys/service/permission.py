# src/apps/v1/sys/service/permission.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : permission.py
# @Software: Cursor
# @Description: 部门服务


from typing import Sequence
from src.apps.v1.sys.crud.permission import crud_permission
from src.apps.v1.sys.models.permission import Permission
from src.common.tree_service import TreeService
from src.database.db_session import AuditAsyncSession


class SvrPermission(TreeService):
    """
    权限服务
    """
    def __init__(self):
        self.crud = crud_permission

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
        return await self.crud.get_permissions_by_role(session, role_ids)


svr_permission = SvrPermission()
