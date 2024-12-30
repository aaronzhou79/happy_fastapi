# src/apps/v1/sys/model.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : model.py
# @Software: Cursor
# @Description: 系统管理数据模型
from typing import Literal

import sqlalchemy as sa

from sqlalchemy import and_
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.data_model.base_model import AuditConfig, DatabaseModel, SoftDeleteMixin
from src.common.data_model.schema_base import generate_schemas
from src.common.enums import UserStatus


class Role(SoftDeleteMixin, DatabaseModel):
    """角色模型"""
    __tablename__: Literal["sys_roles"] = "sys_roles"
    __table_args__ = (
        sa.UniqueConstraint('name', name='ix_sys_roles_unique_name'),
    )

    name: Mapped[str] = mapped_column(sa.String(50), nullable=False, comment="角色名称")
    users: Mapped[list["User"]] = relationship("User", secondary="sys_user_roles", back_populates="roles")


class User(SoftDeleteMixin, DatabaseModel):
    """用户模型"""
    __tablename__: Literal["sys_users"] = "sys_users"
    __table_args__ = (
        sa.UniqueConstraint('name', name='ix_sys_users_unique_name'),
        sa.UniqueConstraint('email', name='ix_sys_users_unique_email'),
    )

    # 启用审计
    audit_config = AuditConfig(
        enabled=True,
        # 只审计这些字段
        fields={'name', 'email', 'role'},
        # 额外忽略这些字段
        exclude_fields={'password'}
    )

    name: Mapped[str] = mapped_column(sa.String(50), nullable=False, comment="用户名")
    email: Mapped[str] = mapped_column(sa.String(120), nullable=False, comment="邮箱")
    password: Mapped[str] = mapped_column(sa.String(128), nullable=False, comment="密码")
    phone: Mapped[str | None] = mapped_column(sa.String(20), nullable=True, comment="手机号")
    user_status: Mapped[UserStatus] = mapped_column(
        sa.Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False, comment="用户状态"
    )
    dept_id: Mapped[int] = mapped_column(sa.ForeignKey("sys_depts.id"), nullable=False, comment="部门ID")
    department: Mapped["Department"] = relationship("Department", back_populates="users")

    roles: Mapped[list["Role"]] = relationship("Role", secondary="sys_user_roles", back_populates="users")

    @property
    def safe_dict(self):
        """返回安全的用户信息（不包含密码）"""
        return self.to_dict(exclude=["password"])


class UserRole(SoftDeleteMixin, DatabaseModel):
    """用户角色模型"""
    __tablename__: Literal["sys_user_roles"] = "sys_user_roles"
    __table_args__ = (
        sa.UniqueConstraint('user_id', 'role_id', name='ix_sys_user_roles_unique_user_role'),
    )

    user_id: Mapped[int] = mapped_column(sa.ForeignKey("sys_users.id"), nullable=False, comment="用户ID")
    role_id: Mapped[int] = mapped_column(sa.ForeignKey("sys_roles.id"), nullable=False, comment="角色ID")


class Department(SoftDeleteMixin, DatabaseModel):
    """部门模型"""
    __tablename__: Literal["sys_depts"] = "sys_depts"
    __table_args__ = (
        sa.UniqueConstraint('name', name='ix_sys_depts_unique_name'),
    )

    # 启用审计
    audit_config = AuditConfig(
        enabled=True,
        # 只审计这些字段
        fields={'name'},
    )

    name: Mapped[str] = mapped_column(sa.String(50), nullable=False, comment="部门名称")
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="department",
        primaryjoin=lambda: and_(
            User.dept_id == Department.id,
            User.deleted_at.is_(None)  # 过滤掉软删除的用户
        )
    )


# 生成 CRUD 模型
DepartmentSchema, DepartmentCreate, DepartmentUpdate = generate_schemas(
    Department,
    include_relationships={"users"}
)

UserSchema, UserCreate, UserUpdate = generate_schemas(
    User,
    include_relationships={"roles"}
)

RoleSchema, RoleCreate, RoleUpdate = generate_schemas(
    Role
)

