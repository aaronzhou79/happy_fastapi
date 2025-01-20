from typing import TYPE_CHECKING, Literal

import sqlalchemy as sa

from sqlmodel import Field, Relationship, SQLModel

from src.common.base_model import DatabaseModel, id_pk
from src.common.enums import PermissionType
from src.common.tree_model import TreeModel

from .role_permission import RolePermission

if TYPE_CHECKING:
    from .role import Role


class PermissionBase(SQLModel):
    """权限基础模型"""
    __tablename__: Literal["sys_permission"] = "sys_permission"

    __table_args__ = (
        sa.Index('idx_permission_parent_id', 'parent_id'),
        sa.Index('idx_permission_route_path', 'route_path'),
        sa.Index('idx_permission_api_path', 'api_path'),
    )

    name: str = Field(..., max_length=50, description="权限名称")
    code: str = Field(..., max_length=50, unique=True, description="权限编码/路由名称")
    type: PermissionType = Field(..., description="权限类型")
    parent_id: int | None = Field(
        default=None,
        foreign_key="sys_permission.id",
        ondelete='RESTRICT',
        description="父权限ID"
    )

    # 路由相关字段
    route_path: str | None = Field(default=None, max_length=200, description="前端路由路径")
    route_component: str | None = Field(default=None, max_length=100, description="前端组件路径")
    route_redirect: str | None = Field(default=None, max_length=200, description="路由重定向路径")
    route_name: str | None = Field(default=None, max_length=50, description="路由名称")
    route_title: str | None = Field(default=None, max_length=50, description="路由标题")
    route_icon: str | None = Field(default=None, max_length=50, description="路由图标")
    route_hidden: bool = Field(default=False, description="是否在菜单中隐藏")
    route_keep_alive: bool = Field(default=True, description="是否缓存该路由")
    route_always_show: bool = Field(default=False, description="是否总是显示根路由")

    # API相关字段
    api_path: str | None = Field(default=None, max_length=200, description="API路径")
    api_method: str | None = Field(default=None, max_length=10, description="HTTP方法")
    perm_code: str | None = Field(default=None, max_length=100, description="权限编码")

    sort_order: int = Field(default=0, description="排序")
    description: str | None = Field(default=None, max_length=200)


class Permission(PermissionBase, TreeModel, DatabaseModel, table=True):
    """权限表"""
    id: id_pk   # type: ignore
    roles: list["Role"] = Relationship(
        back_populates="permissions",
        link_model=RolePermission
    )


class PermissionCreate(PermissionBase):
    """权限创建模型"""


class PermissionUpdate(PermissionBase):
    """权限更新模型"""
    id: int


class PermissionGet(PermissionBase):
    """权限获取模型"""
    id: int
