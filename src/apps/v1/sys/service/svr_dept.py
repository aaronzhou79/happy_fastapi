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
from src.database.db_session import AuditAsyncSession


class SvrDept(BaseService[Dept, DeptCreate, DeptUpdate]):
    """
    部门服务
    """
    def __init__(self):
        super().__init__(crud=crud_dept)
        self.add_hook('before_create', self.before_create)
        self.add_hook('after_create', self.after_create)

    async def before_create(self, session: AuditAsyncSession, obj_in: DeptCreate) -> None:
        """创建前钩子"""
        print(f"Before create: {obj_in}")

    async def after_create(self, session: AuditAsyncSession, obj: Dept) -> None:
        """创建后钩子"""
        print(f"After create: {obj}")


svr_dept = SvrDept()
