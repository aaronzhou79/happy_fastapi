# src/apps/v1/sys/models/role.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : role.py
# @Software: Cursor
# @Description: 角色数据模型
from typing import TYPE_CHECKING, Literal

import sqlalchemy as sa

from sqlmodel import Field, Relationship, SQLModel

from src.apps.v1.sys.models.user_role import UserRole
from src.common.data_model.base_model import DatabaseModel, id_pk
from src.common.enums import RoleStatusType

if TYPE_CHECKING:
    from src.apps.v1.sys.models.user import User


class RoleBase(SQLModel):
    """角色基础模型"""
    __tablename__: Literal["sys_role"] = "sys_role"

    name: str = Field(..., max_length=32)
    code: str = Field(..., max_length=32, unique=True)
    sort: int = Field(default=0)
    status: RoleStatusType = Field(default=RoleStatusType.active)
    description: str | None = Field(default=None, sa_type=sa.Text)


class Role(RoleBase, DatabaseModel, table=True):
    """角色表"""
    __tablename__: Literal["sys_role"] = "sys_role"
    id: id_pk  # type: ignore

    # Relationships
    users: list["User"] = Relationship(back_populates="roles", link_model=UserRole)


class RoleCreate(RoleBase):
    """角色创建模型"""


class RoleUpdate(RoleBase):
    """角色更新模型"""
    id: int
