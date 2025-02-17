# src/apps/v1/sys/service/svr_dept.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : svr_dept.py
# @Software: Cursor
# @Description: 部门服务


from typing import Sequence

from src.apps.v1.sys.crud.permission_rule import crud_permission_rule
from src.apps.v1.sys.models.permission_rule import PermissionRule, PermissionRuleCreate, PermissionRuleUpdate
from src.common.base_service import BaseService
from src.database.db_session import AuditAsyncSession


class SvrPermissionRule(BaseService[PermissionRule, PermissionRuleCreate, PermissionRuleUpdate]):
    """
    权限规则服务
    """
    def __init__(self):
        self.crud = crud_permission_rule
        super().__init__(crud=self.crud)

    async def get_by_permission(self, session: AuditAsyncSession, permission_id: int) -> Sequence[PermissionRule]:
        """获取权限规则"""
        return await self.crud.get_by_permission(session=session, permission_id=permission_id)


svr_permission_rule = SvrPermissionRule()
