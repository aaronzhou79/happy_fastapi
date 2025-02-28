# src/apps/v1/bas/crud/crud_product.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : crud_product.py
# @Software: Cursor
# @Description: 产品信息CRUD类

from typing import Sequence

from sqlmodel import select

from src.apps.v1.bas.models.mdl_product import Product, ProductCreate, ProductUpdate
from src.apps.v1.bas.models.mdl_product_bom import ProductBom
from src.apps.v1.bas.models.mdl_product_bom_wip import ProductBomWip
from src.common.base_crud import CRUDBase
from src.database.db_session import AuditAsyncSession, CurrentSession


class CrudProduct(CRUDBase):
    """产品信息CRUD类"""
    def __init__(self):
        super().__init__(
            model=Product,
            create_model=ProductCreate,
            update_model=ProductUpdate,
        )

    async def get_product(self, session: AuditAsyncSession, product_code: str, ignore_id: int = 0) -> Product:
        """
        根据产品编码获取产品

        :param product_code: 产品编码
        :param ignore_id: 忽略的产品Id
        :return: 相同编码的产品
        """
        query = select(self.model).where(self.model.code == product_code)

        if ignore_id > 0:
            query = query.where(self.model.id != ignore_id)

        result = await session.execute(query)

        return result.scalars().first()

    async def cust_create(self, session: AuditAsyncSession, product: ProductCreate) -> Product:
        """
        自定义新增
        """
        await self.bulk_create(session=session, objects=[product])

        return product

    async def cust_update(self, session: AuditAsyncSession, product: ProductUpdate) -> Product:
        """
        自定义修改
        """
        await self.update(session=session, obj_in=product)

        return product


crud_product = CrudProduct()
