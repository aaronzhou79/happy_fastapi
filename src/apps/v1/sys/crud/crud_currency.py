# src/apps/v1/bas/crud/crud_currency.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : currency.py
# @Software: Cursor
# @Description: 货币信息CRUD类

from sqlmodel import select

from src.apps.v1.bas.models.mdl_currency import Currency, CurrencyCreate, CurrencyUpdate
from src.common.base_crud import CRUDBase
from src.database.db_session import AuditAsyncSession


class CrudCurrency(CRUDBase):
    """货币信息CRUD类"""
    def __init__(self):
        super().__init__(
            model=Currency,
            create_model=CurrencyCreate,
            update_model=CurrencyUpdate,
        )

    async def get_currency(self, session: AuditAsyncSession, code: str, ignore_id: int = 0) -> Currency:
        """
        根据编码获取数据
        """
        query = select(self.model).where(self.model.code == code)

        if ignore_id > 0:
            query = query.where(self.model.id != ignore_id)

        result = await session.execute(query)

        return result.scalars().first()


crud_currency = CrudCurrency()
