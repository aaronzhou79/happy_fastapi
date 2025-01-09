# src/apps/v1/sys/service/svr_dept.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : svr_dept.py
# @Software: Cursor
# @Description: 部门服务


from src.apps.v1.sys.crud.dept import crud_dept
from src.apps.v1.sys.models.dept import Dept, DeptCreate, DeptUpdate
from src.common.base_service import BaseService
from src.common.enums import HookTypeEnum
from src.database.db_session import AuditAsyncSession


class SvrDept(BaseService[Dept, DeptCreate, DeptUpdate]):
    """
    部门服务
    """
    def __init__(self):
        super().__init__(crud=crud_dept)
        self.add_hook(HookTypeEnum.before_create, self.before_create)
        self.add_hook(HookTypeEnum.after_create, self.after_create)
        self.add_hook(HookTypeEnum.before_update, self.before_update)
        self.add_hook(HookTypeEnum.after_update, self.after_update)
        self.add_hook(HookTypeEnum.before_delete, self.before_delete)
        self.add_hook(HookTypeEnum.after_delete, self.after_delete)

    async def before_create(self, session: AuditAsyncSession, obj_in: DeptCreate) -> None:
        """创建前钩子"""
        print(f"Before create: {obj_in}")

    async def after_create(self, session: AuditAsyncSession, db_obj: Dept, obj_in: DeptCreate) -> None:
        """创建后钩子"""
        print(f"After create: {db_obj} | {obj_in}")

    async def before_update(self, session: AuditAsyncSession, db_obj: Dept, obj_in: DeptUpdate) -> None:
        """更新前钩子"""
        print(f"Before update: {db_obj} | {obj_in}")

    async def after_update(self, session: AuditAsyncSession, db_obj: Dept, obj_in: DeptUpdate) -> None:
        """更新后钩子"""
        print(f"After update: {db_obj} | {obj_in}")

    async def before_delete(self, session: AuditAsyncSession, db_obj: Dept) -> None:
        """删除前钩子"""
        print(f"Before delete: {db_obj}")

    async def after_delete(self, session: AuditAsyncSession, db_obj: Dept) -> None:
        """删除后钩子"""
        print(f"After delete: {db_obj}")


svr_dept = SvrDept()
