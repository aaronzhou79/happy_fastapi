# src/apps/v1/sys/model/users.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : users.py
# @Software: Cursor
# @Description: 用户管理数据模型
from typing import TYPE_CHECKING, Literal

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.data_model.base_model import AuditConfig, DatabaseModel, SoftDeleteMixin
from src.common.data_model.schema_base import generate_schemas
from src.common.enums import UserStatus
from src.apps.v1.sys.model.depts import Department

if TYPE_CHECKING:
    from src.apps.v1.sys.model.roles import Role, UserRole


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
    department: Mapped[Department] = relationship(
        "Department",
        back_populates="users"
    )

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary="sys_user_roles",
        back_populates="users",
        primaryjoin=lambda: sa.and_(
            Role.id == UserRole.role_id,
            UserRole.user_id == User.id,
            User.deleted_at.is_(None)  # 过滤掉软删除的用户
        )
    )

    @property
    def safe_dict(self):
        """返回安全的用户信息（不包含密码）"""
        return self.to_dict(exclude=["password"])


UserSchema, UserCreate, UserUpdate = generate_schemas(
    User,
    include_relationships={"roles"}
)