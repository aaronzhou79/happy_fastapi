# src/apps/v1/bas/models/mdl_cost.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : mdl_cost.py
# @Software: Cursor
# @Description: 附加费信息模型

from typing import Literal

from sqlmodel import Field, SQLModel

from src.common.base_models.database_mixin import DatabaseModel
from src.common.base_models.datetime_mixin import DateTimeMixin


class CostBase(SQLModel):
    """附加费信息模型"""

    code: str = Field(..., max_length=32, unique=True, description='费用编码')
    name: str = Field(..., max_length=128, description='费用名称')
    price: float | None = Field(default=None, description='单价')
    uom: str | None = Field(default=None, max_length=32, description='单位')
    valid: bool = Field(default=True, description='是否生效')
    notes: str | None = Field(default=None, description='备注')


class Cost(CostBase, DateTimeMixin, DatabaseModel, table=True):
    """附加费信息表"""

    __tablename__: Literal['bas_cost'] = 'bas_cost'

    # Relationships


class CostCreate(CostBase):
    """附加费信息创建模型"""


class CostUpdate(CostBase):
    """附加费信息更新模型"""

    id: int
