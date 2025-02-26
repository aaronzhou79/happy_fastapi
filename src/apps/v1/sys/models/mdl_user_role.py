# src/apps/v1/sys/models.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : models.py
# @Software: Cursor
# @Description: 系统管理模块数据模型
from typing import Literal

import sqlalchemy as sa

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from src.common.base_models.database_mixin import DatabaseModel
from src.common.base_models.datetime_mixin import DateTimeMixin


class UserRoleBase(DateTimeMixin, SQLModel):
    """用户-角色关联基础模型"""
    user_id: int = Field(default=None, foreign_key="sys_user.id", sa_type=sa.BIGINT, ondelete='CASCADE')
    role_id: int = Field(default=None, foreign_key="sys_role.id", sa_type=sa.BIGINT, ondelete='CASCADE')


class UserRole(UserRoleBase, DatabaseModel, table=True):
    """用户-角色关联表"""
    __tablename__: Literal["sys_user_role"] = "sys_user_role"
    __table_args__ = (UniqueConstraint('user_id', 'role_id', name='uq_user_role'),)


class UserRoleCreate(UserRoleBase):
    """用户-角色关联创建模型"""


class UserRoleUpdate(UserRoleBase):
    """用户-角色关联更新模型"""
