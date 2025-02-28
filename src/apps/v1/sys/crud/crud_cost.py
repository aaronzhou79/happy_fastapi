# src/apps/v1/bas/crud/crud_cost.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : crud_cost.py
# @Software: Cursor
# @Description: 附加费信息CRUD类

from sqlmodel import select

from src.apps.v1.bas.models.mdl_cost import Cost, CostCreate, CostUpdate
from src.common.base_crud import CRUDBase
from src.database.db_session import AuditAsyncSession


class CrudCost(CRUDBase):
    """附加费信息CRUD类"""
    def __init__(self):
        super().__init__(
            model=Cost,
            create_model=CostCreate,
            update_model=CostUpdate,
        )

    async def get_cost(self, session: AuditAsyncSession, code: str, ignore_id: int = 0) -> Cost:
        """
        根据编码获取数据
        """
        query = select(self.model).where(self.model.code == code)

        if ignore_id > 0:
            query = query.where(self.model.id != ignore_id)

        result = await session.execute(query)

        return result.scalars().first()


crud_cost = CrudCost()
