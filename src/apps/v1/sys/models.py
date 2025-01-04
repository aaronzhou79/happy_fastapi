# src/apps/v1/sys/models.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : models.py
# @Software: Cursor
# @Description: 系统管理模块数据模型
from datetime import datetime
from typing import Annotated, Any, Literal

import sqlalchemy as sa

from sqlalchemy import JSON, TEXT, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.common.data_model.base_model import DatabaseModel, SoftDeleteMixin, mapper_registry
from src.common.data_model.base_schema import SchemaType, generate_schema
from src.common.enums import UserStatus


class OperaLog(DatabaseModel):
    """操作日志表"""

    __tablename__: Literal['sys_opera_log'] = 'sys_opera_log'

    trace_id: Mapped[str] = mapped_column(String(32), comment='请求跟踪 ID')
    username: Mapped[str | None] = mapped_column(String(20), comment='用户名')
    method: Mapped[str] = mapped_column(String(20), comment='请求类型')
    title: Mapped[str] = mapped_column(String(255), comment='操作模块')
    path: Mapped[str] = mapped_column(String(500), comment='请求路径')
    ip: Mapped[str] = mapped_column(String(50), comment='IP地址')
    country: Mapped[str | None] = mapped_column(String(50), comment='国家')
    region: Mapped[str | None] = mapped_column(String(50), comment='地区')
    city: Mapped[str | None] = mapped_column(String(50), comment='城市')
    user_agent: Mapped[str] = mapped_column(String(255), comment='请求头')
    os: Mapped[str | None] = mapped_column(String(50), comment='操作系统')
    browser: Mapped[str | None] = mapped_column(String(50), comment='浏览器')
    device: Mapped[str | None] = mapped_column(String(50), comment='设备')
    args: Mapped[str | None] = mapped_column(JSON(), comment='请求参数')
    status: Mapped[int] = mapped_column(comment='操作状态（0异常 1正常）')
    code: Mapped[str] = mapped_column(String(20), insert_default='200', comment='操作状态码')
    msg: Mapped[str | None] = mapped_column(TEXT, comment='提示消息')
    cost_time: Mapped[float] = mapped_column(insert_default=0.0, comment='请求耗时（ms）')
    opera_time: Mapped[datetime] = mapped_column(comment='操作时间')


class Dept(SoftDeleteMixin, DatabaseModel):
    """部门模型"""
    __tablename__: Literal["sys_depts"] = "sys_depts"
    __table_args__ = (
        sa.UniqueConstraint('name', name='ix_sys_depts_unique_name'),
    )

    name: Mapped[str] = mapped_column(sa.String(50), nullable=False, comment="部门名称")
    manager: Mapped[str | None] = mapped_column(sa.String(50), nullable=True, comment="部门经理")
    users = relationship(
        "User",
        back_populates="dept",
        primaryjoin=lambda: sa.and_(
            User.dept_id == Dept.id,
            User.deleted_at.is_(None)
        )
    )


class User(SoftDeleteMixin, DatabaseModel):
    """用户模型"""
    __tablename__: Literal["sys_users"] = "sys_users"
    __table_args__ = (
        sa.UniqueConstraint('name', name='ix_sys_users_unique_name'),
        sa.UniqueConstraint('email', name='ix_sys_users_unique_email'),
    )

    name: Mapped[str] = mapped_column(sa.String(50), nullable=False, comment="用户名")
    email: Mapped[str] = mapped_column(sa.String(120), nullable=False, comment="邮箱")
    password: Mapped[str] = mapped_column(sa.String(128), nullable=False, comment="密码")
    phone: Mapped[str | None] = mapped_column(sa.String(20), nullable=True, comment="手机号")
    user_status: Mapped[UserStatus] = mapped_column(
        sa.Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False, comment="用户状态"
    )
    dept_id: Mapped[int] = mapped_column(sa.ForeignKey("sys_depts.id"), nullable=False, comment="部门ID")
    dept = relationship(
        "Dept",
        back_populates="users",
        primaryjoin=lambda: sa.and_(
            Dept.id == User.dept_id,
            Dept.deleted_at.is_(None)
        )
    )
    roles = relationship(
        "Role",
        secondary="sys_user_roles",
        back_populates="users"
    )


class Role(SoftDeleteMixin, DatabaseModel):
    """角色模型"""
    __tablename__: Literal["sys_roles"] = "sys_roles"
    __table_args__ = (
        sa.UniqueConstraint('name', name='ix_sys_roles_unique_name'),
    )

    name: Mapped[str] = mapped_column(sa.String(50), nullable=False, comment="角色名称")
    users = relationship(
        "User",
        secondary="sys_user_roles",
        back_populates="roles"
    )


class UserRole(SoftDeleteMixin, DatabaseModel):
    """用户角色模型"""
    __tablename__: Literal["sys_user_roles"] = "sys_user_roles"
    __table_args__ = (
        sa.UniqueConstraint('user_id', 'role_id', name='ix_sys_user_roles_unique_user_role'),
    )

    user_id: Mapped[int] = mapped_column(sa.ForeignKey("sys_users.id"), nullable=False, comment="用户ID")
    role_id: Mapped[int] = mapped_column(sa.ForeignKey("sys_roles.id"), nullable=False, comment="角色ID")


mapper_registry.configure()

OperaLogSchemaCreate = generate_schema(OperaLog, SchemaType.CREATE)

DeptSchemaWithUsers = generate_schema(
    Dept, SchemaType.BASE, include_relationships=["users"]
)
DeptSchemaBase = generate_schema(Dept, SchemaType.BASE)
DeptSchemaUpdate = generate_schema(Dept, SchemaType.UPDATE)
DeptSchemaCreate = generate_schema(Dept, SchemaType.CREATE)

UserSchemaBase = generate_schema(User, SchemaType.BASE, include_relationships=["roles", "dept"])
UserSchemaUpdate = generate_schema(User, SchemaType.UPDATE)
UserSchemaCreate = generate_schema(User, SchemaType.CREATE, include_relationships=["roles"])

RoleSchemaBase = generate_schema(Role, SchemaType.BASE)
RoleSchemaUpdate = generate_schema(Role, SchemaType.UPDATE)
RoleSchemaCreate = generate_schema(Role, SchemaType.CREATE)
