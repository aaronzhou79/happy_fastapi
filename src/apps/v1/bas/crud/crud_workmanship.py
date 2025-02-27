# src/apps/v1/bas/crud/crud_workmanship.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : crud_workmanship.py
# @Software: Cursor
# @Description: 工艺信息CRUD类

from sqlmodel import select

from src.apps.v1.bas.models.mdl_workmanship import Workmanship, WorkmanshipCreate, WorkmanshipUpdate
from src.common.base_crud import CRUDBase
from src.database.db_session import AuditAsyncSession


class CrudWorkmanship(CRUDBase):
    """工艺信息CRUD类"""
    def __init__(self):
        super().__init__(
            model=Workmanship,
            create_model=WorkmanshipCreate,
            update_model=WorkmanshipUpdate,
        )

    async def get_workmanship(self, session: AuditAsyncSession, code: str, ignore_id: int = 0) -> Workmanship:
        """
        根据编码获取数据
        """
        query = select(self.model).where(self.model.code == code)

        if ignore_id > 0:
            query = query.where(self.model.id != ignore_id)

        result = await session.execute(query)

        return result.scalars().first()


crud_workmanship = CrudWorkmanship()
