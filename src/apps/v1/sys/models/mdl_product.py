# src/apps/v1/bas/models/mdl_product.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : mdl_product.py
# @Software: Cursor
# @Description: 产品信息模型

from typing import Any, Literal

from sqlmodel import Field, Relationship, SQLModel

from src.apps.v1.bas.models.mdl_product_bom import ProductBom, ProductBomCreate
from src.apps.v1.bas.models.mdl_product_bom_wip import ProductBomWipCreate
from src.common.base_models.database_mixin import DatabaseModel
from src.common.base_models.datetime_mixin import DateTimeMixin


class ProductBase(SQLModel):
    """产品信息模型"""

    code: str | None = Field(default=None, max_length=128, description='产品编码')
    name: str | None = Field(default=None, max_length=128, description='产品名称')
    alias: str | None = Field(default=None, max_length=128, description='产品别名')
    category: str | None = Field(default=None, max_length=32, description='产品类型')
    sort: str | None = Field(default=None, max_length=32, description='二级分类')
    workmanship: str | None = Field(default=None, max_length=32, description='工艺')
    price: float | None = Field(default=None, description='单价')
    colour: str | None = Field(default=None, max_length=32, description='颜色')
    shape: str | None = Field(default=None, max_length=32, description='形状')
    length: float | None = Field(default=None, description='长')
    width: float | None = Field(default=None, description='宽')
    height: float | None = Field(default=None, description='高')
    actual_area: float | None = Field(default=None, description='实际面积')
    sales_area: float | None = Field(default=None, description='结算面积')
    gross_weight: float | None = Field(default=None, description='毛重')
    net_weight: float | None = Field(default=None, description='净重')
    product_deep: float | None = Field(default=None, description='产品厚度')
    rm_deep: float | None = Field(default=None, description='原料厚度')
    al_bar_deep: float | None = Field(default=None, description='铝条厚度')
    film_deep: float | None = Field(default=None, description='胶片厚度')
    composite: bool | None = Field(default=None, description='复合玻璃')
    uom: str | None = Field(default=None, max_length=32, description='单位')
    material_code: str | None = Field(default=None, max_length=128, description='材料编码')
    material_name: str | None = Field(default=None, max_length=128, description='材料名称')
    specs: str | None = Field(default=None, max_length=128, description='规格')
    pricing_mode: str | None = Field(default=None, max_length=32, description='计价方式')
    expand1: str | None = Field(default=None, description='扩展字段1')
    expand2: str | None = Field(default=None, description='扩展字段2')
    expand3: str | None = Field(default=None, description='扩展字段3')
    smg_flag: bool | None = Field(default=None, description='半成品标记')
    valid: bool | None = Field(default=None, description='生效')
    notes: str | None = Field(default=None, description='备注')


class Product(ProductBase, DateTimeMixin, DatabaseModel, table=True):
    """产品信息表"""

    __tablename__: Literal['bas_product'] = 'bas_product'

    # Relationships
    boms: list['ProductBom'] = Relationship()


class ProductCreate(ProductBase):
    """产品信息创建模型"""
    id: int
    boms: list[ProductBomCreate]
    wips: list[ProductBomWipCreate]

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """自定义序列化方法，排除字段"""
        exclude = kwargs.get('exclude', set())
        exclude.add('boms')
        exclude.add('wips')
        kwargs['exclude'] = exclude
        return super().model_dump(**kwargs)


class ProductUpdate(ProductBase):
    """产品信息更新模型"""
    id: int
    boms: list[ProductBomCreate]
    wips: list[ProductBomWipCreate]

    def model_dump(self, **kwargs) -> dict[str, Any]:
        """自定义序列化方法，排除字段"""
        exclude = kwargs.get('exclude', set())
        exclude.add('boms')
        exclude.add('wips')
        kwargs['exclude'] = exclude
        return super().model_dump(**kwargs)
