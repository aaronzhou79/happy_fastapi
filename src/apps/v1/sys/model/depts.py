# src/apps/v1/sys/model/opera_log.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : department.py
# @Software: Cursor
# @Description: 部门管理数据模型
from typing import TYPE_CHECKING, Literal

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.data_model.base_model import DatabaseModel, SoftDeleteMixin
from src.common.data_model.schema_base import generate_schemas

from src.apps.v1.sys.model.users import User


class Department(SoftDeleteMixin, DatabaseModel):
    """部门模型"""
    __tablename__: Literal["sys_depts"] = "sys_depts"
    __table_args__ = (
        sa.UniqueConstraint('name', name='ix_sys_depts_unique_name'),
    )

    name: Mapped[str] = mapped_column(sa.String(50), nullable=False, comment="部门名称")
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="department",
        primaryjoin=lambda: sa.and_(
            sa.text('sys_users.dept_id = sys_depts.id'),
            sa.text('sys_users.deleted_at IS NULL')
        )
    )


# 生成 CRUD 模型
DepartmentSchema, DepartmentCreate, DepartmentUpdate = generate_schemas(
    Department,
    include_relationships={"users"}
)