# src/apps/v1/bas/crud/crud_customer_site.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/2/8
# @Author  : lei
# @File    : crud_customer_site.py
# @Software: Cursor
# @Description: 客户工地信息相关CRUD类

from typing import Sequence

from sqlmodel import delete

from src.apps.v1.bas.models.mdl_customer_site import CustomerSite, CustomerSiteCreate, CustomerSiteUpdate
from src.common.base_crud import CRUDBase
from src.database.db_session import AuditAsyncSession


class CrudCustomerSite(CRUDBase):
    """客户工地信息相关CRUD类"""
    def __init__(self):
        super().__init__(
            model=CustomerSite,
            create_model=CustomerSiteCreate,
            update_model=CustomerSiteUpdate,
        )

    async def sync_customer_sites(self, session: AuditAsyncSession,
                          customer_id: int,
                          sitrs: list[CustomerSiteCreate]) -> None:
        """
        同步客户工地
        """
        result = delete(CustomerSite).where(CustomerSite.customer_id == customer_id)
        await session.execute(result)
        await session.flush()

        await self.bulk_create(session=session, objects=sitrs)


crud_customer_site = CrudCustomerSite()
