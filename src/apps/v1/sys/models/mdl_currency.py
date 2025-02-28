# src/apps/v1/bas/models/mdl_currency.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : mdl_currency.py
# @Software: Cursor
# @Description: 货币信息模型

from typing import Literal

from sqlmodel import Field, SQLModel

from src.common.base_models.database_mixin import DatabaseModel
from src.common.base_models.datetime_mixin import DateTimeMixin


class CurrencyBase(SQLModel):
    """货币信息模型"""

    code: str = Field(..., max_length=32, unique=True, description='货币编码')
    name: str = Field(..., max_length=32, description='货币名称')
    alias: str | None = Field(default=None, max_length=32, description='货币别名')
    symbol: str | None = Field(default=None, max_length=32, description='货币符号')
    exchange_rate: float = Field(default=1, description='汇率')
    valid: bool = Field(default=True, description='是否生效')
    notes: str | None = Field(default=None, description='备注')


class Currency(CurrencyBase, DateTimeMixin, DatabaseModel, table=True):
    """货币信息表"""

    __tablename__: Literal['bas_currency'] = 'bas_currency'

    # Relationships


class CurrencyCreate(CurrencyBase):
    """货币信息创建模型"""


class CurrencyUpdate(CurrencyBase):
    """货币信息更新模型"""

    id: int
