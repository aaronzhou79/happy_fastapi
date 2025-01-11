from typing import TYPE_CHECKING, Literal

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

    name: str = Field(..., max_length=50, description="权限名称")
    code: str = Field(..., max_length=50, unique=True, description="权限编码")
    type: PermissionType = Field(..., description="权限类型")
    parent_id: int | None = Field(default=None, foreign_key="sys_permission.id")
    api_path: str | None = Field(default=None, max_length=200, description="API路径")
    api_method: str | None = Field(default=None, max_length=10, description="HTTP方法")
    component: str | None = Field(default=None, max_length=100, description="前端组件")
    perm_code: str | None = Field(default=None, max_length=100, description="权限编码")
    icon: str | None = Field(default=None, max_length=50, description="图标")
    sort_order: int = Field(default=0, description="排序")
    is_visible: bool = Field(default=True, description="是否可见")
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
