# src/apps/v1/bas/models/mdl_workmanship.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : mdl_workmanship.py
# @Software: Cursor
# @Description: 工艺信息模型

from typing import Literal

from sqlmodel import Field, SQLModel

from src.common.base_models.database_mixin import DatabaseModel
from src.common.base_models.datetime_mixin import DateTimeMixin


class WorkmanshipBase(SQLModel):
    """工艺信息模型"""

    code: str = Field(..., max_length=32, unique=True, description='工艺编码')
    name: str = Field(..., max_length=128, unique=True, description='工艺名称')
    alias: str | None = Field(default=None, max_length=128, description='工艺别名')
    seq_no: int | None = Field(default=0, description='工艺序号')
    type: str = Field(..., max_length=32, description='工序类型')
    pricing_mode: str = Field(..., max_length=32, description='计价方式')
    price: float | None = Field(default=None, description='单价')
    uom: str | None = Field(default=None, max_length=32, description='加工单位')
    is_charge: bool = Field(default=False, description='收费工艺')
    is_handover: bool = Field(default=True, description='交接工艺')
    smg_out_flag: bool = Field(default=False, description='半成品出库工艺')
    valid: bool = Field(default=True, description='生效')
    notes: str | None = Field(default=None, description='备注')


class Workmanship(WorkmanshipBase, DateTimeMixin, DatabaseModel, table=True):
    """工艺信息表"""

    __tablename__: Literal['bas_workmanship'] = 'bas_workmanship'

    # Relationships


class WorkmanshipCreate(WorkmanshipBase):
    """工艺信息创建模型"""


class WorkmanshipUpdate(WorkmanshipBase):
    """工艺信息更新模型"""

    id: int
