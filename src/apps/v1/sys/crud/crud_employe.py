# src/apps/v1/bas/crud/crud_employe.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : crud_employe.py
# @Software: Cursor
# @Description: 员工档案CRUD类

from sqlmodel import select

from src.apps.v1.bas.models.mdl_employe import Employe, EmployeCreate, EmployeUpdate
from src.common.base_crud import CRUDBase
from src.database.db_session import AuditAsyncSession


class CrudEmploye(CRUDBase):
    """员工档案CRUD类"""
    def __init__(self):
        super().__init__(
            model=Employe,
            create_model=EmployeCreate,
            update_model=EmployeUpdate,
        )

    async def get_employe(self, session: AuditAsyncSession, employe_no: str, ignore_id: int = 0) -> Employe:
        """
        根据编码获取数据
        """
        query = select(self.model).where(self.model.employe_no == employe_no)

        if ignore_id > 0:
            query = query.where(self.model.id != ignore_id)

        result = await session.execute(query)

        return result.scalars().first()


crud_employe = CrudEmploye()
