# src/apps/v1/bas/models/mdl_product_bom.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : mdl_product_bom.py
# @Software: Cursor
# @Description: 产品Bom模型

from typing import Literal

import sqlalchemy as sa

from sqlmodel import Field, Relationship, SQLModel

from src.apps.v1.bas.models.mdl_product_bom_wip import ProductBomWip, ProductBomWipCreate, ProductBomWipUpdate
from src.common.base_models.database_mixin import DatabaseModel
from src.common.enums import ProductBomType


class ProductBomBase(SQLModel):
    """产品Bom模型"""

    product_id: int = Field(..., foreign_key="bas_product.id", ondelete='CASCADE', description="产品ID")
    parent_id: int = Field(..., description="父级Bom")

    code: str = Field(..., max_length=128, description='Bom编码')
    name: str = Field(..., max_length=128, description='Bom名称')
    level: int = Field(..., description='层级')
    type: ProductBomType = Field(default=ProductBomType.FP, description="Bom层类型")
    flag: str = Field(..., max_length=32, description='片标记')
    material_deep: float | None = Field(default=None, description='物料厚度')
    use_qty: float | None = Field(default=None, description='用量')
    uom: str | None = Field(default=None, max_length=32, description='单位')
    wip_codes: str | None = Field(default=None, max_length=512, description='工艺编码汇总')
    wip_names: str | None = Field(default=None, max_length=512, description='工艺名称汇总')
    work_content: str | None = Field(default=None, max_length=512, description='加工要求')
    is_setting: bool = Field(default=True, description='是否需要设置工序')
    composite: bool = Field(default=False, description='复合层')
    length: float | None = Field(default=None, description='长')
    width: float | None = Field(default=None, description='宽')
    height: float | None = Field(default=None, description='高')
    notes: str | None = Field(default=None, description='备注')


class ProductBom(ProductBomBase, DatabaseModel, table=True):
    """产品BOM表"""

    __tablename__: Literal['bas_product_bom'] = 'bas_product_bom'

    # Relationships

    wips: list['ProductBomWip'] = Relationship()


class ProductBomCreate(ProductBomBase):
    """产品BOM创建模型"""
    id: int
    wips: list[ProductBomWipCreate]
    children: list["ProductBomCreate"]


class ProductBomUpdate(ProductBomBase):
    """产品BOM更新模型"""

    id: int
    wips: list[ProductBomWipUpdate]
    children: list["ProductBomUpdate"]
