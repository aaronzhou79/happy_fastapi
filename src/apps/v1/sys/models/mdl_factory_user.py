# src/apps/v1/sys/models/factory_user.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : factory_user.py
# @Software: Cursor
# @Description: 工厂用户模型
from typing import Literal

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from src.common.base_models.database_mixin import DatabaseModel
from src.common.base_models.datetime_mixin import DateTimeMixin


class FactoryUserBase(SQLModel):
    """工厂用户模型"""

    user_id: int = Field(default=None, foreign_key="sys_user.id", ondelete='CASCADE')
    factory_id: int = Field(default=None, foreign_key="sys_factory.id", ondelete='CASCADE')


class FactoryUser(FactoryUserBase, DateTimeMixin, DatabaseModel, table=True):
    """工厂用户表"""

    __tablename__: Literal['sys_factory_user'] = 'sys_factory_user'
    __table_args__ = (UniqueConstraint('user_id', 'factory_id', name='uq_factory_user'),)

    # Relationships


class FactoryUserCreate(FactoryUserBase):
    """工厂用户创建模型"""


class FactoryUserUpdate(FactoryUserBase):
    """工厂用户更新模型"""

    id: int
