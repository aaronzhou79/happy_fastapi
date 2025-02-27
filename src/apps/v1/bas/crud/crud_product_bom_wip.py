# src/apps/v1/bas/crud/crud_product_bom_wip.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : crud_product_bom_wip.py
# @Software: Cursor
# @Description: 产品Bom工艺信息CRUD类

from sqlmodel import delete

from src.apps.v1.bas.models.mdl_product_bom_wip import ProductBomWip, ProductBomWipCreate, ProductBomWipUpdate
from src.common.base_crud import CRUDBase
from src.database.db_session import AuditAsyncSession, CurrentSession


class CrudProductBomWip(CRUDBase):
    """产品Bom工艺信息CRUD类"""
    def __init__(self):
        super().__init__(
            model=ProductBomWip,
            create_model=ProductBomWipCreate,
            update_model=ProductBomWipUpdate,
        )

    async def sync_product_boms_wip(self, session: AuditAsyncSession,
                          product_id: int,
                          wips: list[ProductBomWipCreate]) -> None:
        """
        同步产品Bom工艺
        """
        result = delete(ProductBomWip).where(ProductBomWip.product_id == product_id)
        await session.execute(result)
        await session.flush()

        await self.bulk_create(session=session, objects=wips)

    async def get_product_wips(self, session: CurrentSession, product_id: int) -> list[ProductBomWip]:
        """
        根据产品编码获取产品wips

        :param product_id: 产品Id
        :return: 产品Bom集合
        """
        return await self.get_by_fields(session=session, product_id=product_id)


crud_wip = CrudProductBomWip()
