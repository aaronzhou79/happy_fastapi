# src/apps/v1/sys/models/factory.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : factory.py
# @Software: Cursor
# @Description: 工厂信息模型

from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal

import sqlalchemy as sa

from sqlmodel import Field, Relationship, SQLModel

from src.apps.v1.sys.models.mdl_factory_user import FactoryUser
from src.common.base_models.database_mixin import DatabaseModel
from src.common.base_models.datetime_mixin import DateTimeMixin

if TYPE_CHECKING:
    from src.apps.v1.sys.models.mdl_user import User


class FactoryBase(SQLModel):
    """工厂信息模型"""

    factory_name: str | None = Field(default=None, max_length=128, description='厂别名称')
    factory_alias: str | None = Field(default=None, max_length=128, description='厂别别名')
    logo: str | None = Field(default=None, max_length=128, description='Logo图片地址')
    is_default: bool = Field(default=False, description='默认厂别')
    sales_type: int = Field(default=1, description='销售类型 1.以销带产 2.以产代销')
    standard_money: str = Field(default='RMB', max_length=32, description='本位币')
    address: str | None = Field(default=None, max_length=512, description='工厂地址')


class Factory(FactoryBase, DateTimeMixin, DatabaseModel, table=True):
    """工厂信息表"""

    __tablename__: Literal['sys_factory'] = 'sys_factory'

    # Relationships
    users: list["User"] = Relationship(back_populates="factorys", link_model=FactoryUser)


class FactoryCreate(FactoryBase):
    """工厂信息创建模型"""


class FactoryUpdate(FactoryBase):
    """工厂信息更新模型"""
    id: int
