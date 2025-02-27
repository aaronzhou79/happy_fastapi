# src/apps/v1/sys/models/mdl_layout.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-14
# @Author  : lei
# @File    : mdl_layout.py
# @Software: Cursor
# @Description: 页面布局模型

from typing import Any, Literal

from sqlmodel import Field, SQLModel

from src.common.base_models.database_mixin import DatabaseModel
from src.common.base_models.datetime_mixin import DateTimeMixin


class LayoutBase(SQLModel):
    """页面布局模型"""

    user_id: str = Field(default=None, foreign_key="sys_user.id", ondelete='CASCADE', description="用户Id")
    tag: str = Field(default=None, max_length=128, description='标记')
    content: str | None = Field(default=None, description='布局内容')
    type: int | None = Field(default=None, description='类型 1.表格 2.表单')
    seq_no: int | None = Field(default=None, description='序号')
    state: int | None = Field(default=None, description='状态')
    fixed: str | None = Field(default=None, max_length=64, description='冻结')
    width: str | None = Field(default=None, max_length=64, description='宽度')
    sort: int | None = Field(default=None, description='排序 1.Asc 2.Desc')


class Layout(LayoutBase, DateTimeMixin, DatabaseModel, table=True):
    """页面布局表"""

    __tablename__: Literal['sys_layout'] = 'sys_layout'

    # Relationships


class LayoutCreate(LayoutBase):
    """页面布局创建模型"""


class LayoutUpdate(LayoutBase):
    """页面布局更新模型"""

    id: int
