# src/apps/v1/bas/models/mdl_material.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : mdl_material.py
# @Software: Cursor
# @Description: 物料信息模型

from typing import Literal

from sqlmodel import Field, SQLModel

from src.common.base_models.database_mixin import DatabaseModel


class MaterialBase(SQLModel):
    """物料信息模型"""

    code: str = Field(..., max_length=32, unique=True, index=True, description='物料编码')
    name: str = Field(..., max_length=128, description='物料名称')
    alias: str | None = Field(default=None, max_length=128, description='物料别名')
    category: str | None = Field(default=None, max_length=128, description='类别')
    item_sort: str | None = Field(default=None, max_length=32, description='二级分类')
    colour: str | None = Field(default=None, max_length=128, description='颜色')
    place_origin: str | None = Field(default=None, max_length=128, description='产地')
    brand: str | None = Field(default=None, max_length=128, description='品牌')
    grade: str | None = Field(default=None, max_length=128, description='等级')
    deep: float | None = Field(default=None, description='厚度')
    pricing_mode: str | None = Field(default=None, max_length=32, description='计价方式')
    price: float | None = Field(default=None, description='单价')
    uom: str | None = Field(default=None, max_length=32, description='单位')
    conversion_ratio: float | None = Field(default=None, description='换算比率')
    base_uom: str | None = Field(default=None, max_length=32, description='基本单位')
    specs: str | None = Field(default=None, max_length=128, description='规格')
    length: float | None = Field(default=None, description='长')
    width: float | None = Field(default=None, description='宽')
    height: float | None = Field(default=None, description='高')
    valid: bool = Field(default=True, description='是否生效')
    notes: str | None = Field(default=None, description='备注')


class Material(MaterialBase, DatabaseModel, table=True):
    """物料信息表"""

    __tablename__: Literal['bas_material'] = 'bas_material'

    # Relationships


class MaterialCreate(MaterialBase):
    """物料信息创建模型"""


class MaterialUpdate(MaterialBase):
    """物料信息更新模型"""

    id: int
