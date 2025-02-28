# src/apps/v1/bas/models/mdl_product_bom_wip.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : mdl_product_bom_wip.py
# @Software: Cursor
# @Description: 产品BOM工艺模型

from typing import Literal

from sqlmodel import Field, SQLModel

from src.common.base_models.database_mixin import DatabaseModel


class ProductBomWipBase(SQLModel):
    """产品BOM工艺模型"""

    bom_id: int = Field(..., foreign_key="bas_product_bom.id", ondelete='CASCADE', description="BomId")
    product_id: int = Field(..., description="产品Id")
    code: str | None = Field(default=None, max_length=128, description='工艺编码')
    name: str | None = Field(default=None, max_length=128, description='工艺名称')
    type: str | None = Field(default=None, max_length=32, description='工艺类型')
    seq_no: int | None = Field(default=None, description='工艺顺序')


class ProductBomWip(ProductBomWipBase, DatabaseModel, table=True):
    """产品BOM工艺表"""

    __tablename__: Literal['bas_product_bom_wip'] = 'bas_product_bom_wip'

    # Relationships


class ProductBomWipCreate(ProductBomWipBase):
    """产品BOM工艺创建模型"""
    id: int


class ProductBomWipUpdate(ProductBomWipBase):
    """产品BOM工艺更新模型"""

    id: int
