# src/apps/v1/sys/models/mdl_user_tenant.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/02/27
# @Author  : Aaron Zhou
# @File    : mdl_user_tenant.py
# @Software: Cursor
# @Description: 系统管理模块数据模型
from typing import Literal

import sqlalchemy as sa

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from src.common.base_models.database_mixin import DatabaseModel
from src.common.base_models.datetime_mixin import DateTimeMixin


class UserTenantBase(DateTimeMixin, SQLModel):
    """用户-账套关联基础模型"""

    user_id: int = Field(
        default=None, foreign_key="sys_user.id", sa_type=sa.BIGINT, ondelete="CASCADE"
    )
    tenant_id: int = Field(
        default=None, foreign_key="sys_tenant.id", sa_type=sa.BIGINT, ondelete="CASCADE"
    )


class UserTenant(UserTenantBase, DatabaseModel, table=True):
    """用户-账套关联表"""

    __tablename__: Literal["sys_user_tenant"] = "sys_user_tenant"
    __table_args__ = (UniqueConstraint("user_id", "tenant_id", name="uq_user_tenant"),)


class UserTenantCreate(UserTenantBase):
    """用户-账套关联创建模型"""


class UserTenantUpdate(UserTenantBase):
    """用户-账套关联更新模型"""

    id: int = Field(..., description="用户-账套关联ID")
