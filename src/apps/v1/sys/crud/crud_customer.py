# src/apps/v1/bas/crud/crud_customer.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/2/8
# @Author  : lei
# @File    : crud_customer.py
# @Software: Cursor
# @Description: 客户信息相关CRUD类

from typing import Sequence

from sqlmodel import delete, select

from src.apps.v1.bas.models.mdl_customer import Customer, CustomerCreate, CustomerUpdate
from src.apps.v1.bas.models.mdl_customer_site import CustomerSite, CustomerSiteCreate
from src.common.base_crud import CRUDBase
from src.database.db_session import AuditAsyncSession


class CrudCustomer(CRUDBase):
    """客户信息相关CRUD类"""
    def __init__(self):
        super().__init__(
            model=Customer,
            create_model=CustomerCreate,
            update_model=CustomerUpdate,
        )

    async def get_customer(self, session: AuditAsyncSession, code: str, ignore_id: int = 0) -> str:
        """
        获取相同编码客户

        :param code: 客户编码
        :param ignore_id: 客户Id
        :return: 已存在的相同编码的客户
        """
        result = await session.execute(
            select(self.model.name)
            .where(self.model.code == code)
            .where(self.model.id != ignore_id)
        )

        return result.scalars().first()


crud_customer = CrudCustomer()
