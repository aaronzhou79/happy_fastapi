# src/apps/v1/bas/models/mdl_dict_type.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-19
# @Author  : lei
# @File    : mdl_dict_type.py
# @Software: Cursor
# @Description: 字典类型模型

from typing import Literal

from sqlmodel import Field, SQLModel

from src.common.base_models.database_mixin import DatabaseModel
from src.common.base_models.datetime_mixin import DateTimeMixin


class DictTypeBase(SQLModel):
    """字典类型模型"""

    code: str = Field(..., min_length=1, max_length=128, unique=True, description='字典类型编码')
    name: str = Field(..., min_length=1, max_length=128, description='字典名称')
    valid: bool = Field(default=True, description='是否生效')
    notes: str | None = Field(default=None, max_length=512, description='备注')
    custom_sql: str | None = Field(default=None, max_length=512, description='自定义查询SQL')


class DictType(DictTypeBase, DateTimeMixin, DatabaseModel, table=True):
    """字典类型表"""

    __tablename__: Literal['bas_dict_type'] = 'bas_dict_type'

    # Relationships


class DictTypeCreate(DictTypeBase):
    """字典类型创建模型"""


class DictTypeUpdate(DictTypeBase):
    """字典类型更新模型"""

    id: int
