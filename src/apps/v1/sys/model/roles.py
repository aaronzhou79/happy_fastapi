# src/apps/v1/sys/model.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : model.py
# @Software: Cursor
# @Description: 角色管理数据模型
from typing import TYPE_CHECKING, Literal

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.data_model.base_model import DatabaseModel, SoftDeleteMixin
from src.common.data_model.schema_base import generate_schemas

if TYPE_CHECKING:
    from src.apps.v1.sys.model.users import User


class Role(SoftDeleteMixin, DatabaseModel):
    """角色模型"""
    __tablename__: Literal["sys_roles"] = "sys_roles"
    __table_args__ = (
        sa.UniqueConstraint('name', name='ix_sys_roles_unique_name'),
    )

    name: Mapped[str] = mapped_column(sa.String(50), nullable=False, comment="角色名称")
    users: Mapped[list['User']] = relationship("User", secondary="sys_user_roles", back_populates="roles")


class UserRole(SoftDeleteMixin, DatabaseModel):
    """用户角色模型"""
    __tablename__: Literal["sys_user_roles"] = "sys_user_roles"
    __table_args__ = (
        sa.UniqueConstraint('user_id', 'role_id', name='ix_sys_user_roles_unique_user_role'),
    )

    user_id: Mapped[int] = mapped_column(sa.ForeignKey("sys_users.id"), nullable=False, comment="用户ID")
    role_id: Mapped[int] = mapped_column(sa.ForeignKey("sys_roles.id"), nullable=False, comment="角色ID")


RoleSchema, RoleCreate, RoleUpdate = generate_schemas(
    Role
)

