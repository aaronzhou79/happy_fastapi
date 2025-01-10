from typing import Literal
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel
from src.common.base_model import DatabaseModel, id_pk

class RolePermissionBase(SQLModel):
    """角色-权限关联基础模型"""
    __tablename__: Literal["sys_role_permission"] = "sys_role_permission"

    role_id: int = Field(..., foreign_key="sys_role.id")
    permission_id: int = Field(..., foreign_key="sys_permission.id")


class RolePermission(RolePermissionBase, DatabaseModel, table=True):
    """角色-权限关联表"""
    __table_args__ = (UniqueConstraint('role_id', 'permission_id'),)
    id: id_pk   # type: ignore


class RolePermissionCreate(RolePermissionBase):
    """角色权限关联创建模型"""


class RolePermissionUpdate(RolePermissionBase):
    """角色权限关联更新模型"""
    id: int