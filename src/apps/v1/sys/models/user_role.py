# src/apps/v1/sys/models.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : models.py
# @Software: Cursor
# @Description: 系统管理模块数据模型
from typing import Literal

from sqlmodel import Field, SQLModel

from src.common.data_model.base_model import DatabaseModel


# ------------------------------ UserRole ------------------------------
class UserRoleBase(SQLModel):
    """用户-角色关联基础模型"""
    user_id: int = Field(default=None, foreign_key="sys_user.id", primary_key=True)
    role_id: int = Field(default=None, foreign_key="sys_role.id", primary_key=True)


class UserRole(UserRoleBase, DatabaseModel, table=True):
    """用户-角色关联表"""
    __tablename__: Literal["sys_user_role"] = "sys_user_role"


class UserRoleCreate(UserRoleBase):
    """用户-角色关联创建模型"""


class UserRoleUpdate(UserRoleBase):
    """用户-角色关联更新模型"""
