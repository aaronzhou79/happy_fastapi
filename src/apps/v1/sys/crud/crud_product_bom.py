# src/apps/v1/bas/crud/crud_product_bom.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : crud_product_bom.py
# @Software: Cursor
# @Description: 产品Bom信息CRUD类

from sqlmodel import delete, select

from src.apps.v1.bas.models.mdl_product_bom import ProductBom, ProductBomCreate, ProductBomUpdate
from src.common.base_crud import CRUDBase
from src.database.db_session import AuditAsyncSession, CurrentSession


class CrudProductBom(CRUDBase):
    """产品Bom信息CRUD类"""
    def __init__(self):
        super().__init__(
            model=ProductBom,
            create_model=ProductBomCreate,
            update_model=ProductBomUpdate,
        )

    async def sync_product_boms(self, session: AuditAsyncSession,
                          product_id: int,
                          boms: list[ProductBomCreate]) -> None:
        """
        同步产品Bom
        """
        result = delete(ProductBom).where(ProductBom.product_id == product_id)
        await session.execute(result)
        await session.flush()

        await self.bulk_create(session=session, objects=boms)

    async def get_product_boms(self, session: CurrentSession, product_id: int) -> list[ProductBom]:
        """
        根据产品编码获取产品boms

        :param product_id: 产品Id
        :return: 产品Bom集合
        """
        return await self.get_by_fields(session=session, product_id=product_id)


crud_bom = CrudProductBom()
