# src/apps/v1/sys/crud/permission_rule.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/01/10
# @Author  : Aaron Zhou
# @File    : permission_rule.py
# @Software: Cursor
# @Description: 权限规则相关CRUD类
from typing import Sequence

from sqlmodel import select

from src.apps.v1.sys.models.permission_rule import PermissionRule, PermissionRuleCreate, PermissionRuleUpdate
from src.common.base_crud import CRUDBase
from src.database.db_session import AuditAsyncSession


class CrudPermissionRule(CRUDBase):
    """权限规则相关CRUD类"""
    def __init__(self):
        super().__init__(
            model=PermissionRule,
            create_model=PermissionRuleCreate,
            update_model=PermissionRuleUpdate,
        )

    async def get_by_permission(self, session: AuditAsyncSession, permission_id: int) -> Sequence[PermissionRule]:
        """获取权限规则"""
        result = await session.execute(
            select(self.model).where(
                self.model.permission_id == permission_id))
        return result.scalars().all()


crud_permission_rule = CrudPermissionRule()
