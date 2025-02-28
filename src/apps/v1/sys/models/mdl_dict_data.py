# src/apps/v1/bas/models/mdl_dict_data.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-19
# @Author  : lei
# @File    : mdl_dict_data.py
# @Software: Cursor
# @Description: 字典数据模型

from typing import Literal

from sqlmodel import Field, SQLModel

from src.common.base_models.database_mixin import DatabaseModel
from src.common.base_models.datetime_mixin import DateTimeMixin


class DictDataBase(SQLModel):
    """字典数据模型"""

    dict_id: int | None = Field(default=None, foreign_key="bas_dict_type.id", ondelete='CASCADE')
    code: str = Field(..., max_length=100, description='字典类型')
    sort: int = Field(default=1, description='字典排序')
    title: str = Field(..., min_length=1, max_length=128, description='字典标签')
    value1: str | None = Field(default=None, max_length=512, description='扩展值1')
    value2: str | None = Field(default=None, max_length=512, description='扩展值2')
    value3: str | None = Field(default=None, max_length=512, description='扩展值3')
    css_class: str | None = Field(default=None, max_length=128, description='样式属性（其他样式扩展）')
    list_class: str | None = Field(default=None, max_length=128, description='表格回显样式')
    is_default: bool = Field(default=False, description='是否默认选中')
    valid: bool = Field(default=True, description='是否生效')
    notes: str | None = Field(default=None, max_length=512, description='备注')


class DictData(DictDataBase, DateTimeMixin, DatabaseModel, table=True):
    """字典数据表"""

    __tablename__: Literal['bas_dict_data'] = 'bas_dict_data'

    # Relationships


class DictDataCreate(DictDataBase):
    """字典数据创建模型"""


class DictDataUpdate(DictDataBase):
    """字典数据更新模型"""

    id: int
