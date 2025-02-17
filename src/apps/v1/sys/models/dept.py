from typing import TYPE_CHECKING, Literal

import sqlalchemy as sa

from sqlmodel import Field, Relationship, SQLModel

from src.common.base_model import DatabaseModel, DateTimeMixin, id_pk
from src.common.tree_model import TreeModel

if TYPE_CHECKING:
    from src.apps.v1.sys.models.user import User


class DeptBase(DateTimeMixin, SQLModel):
    """部门基础模型"""
    # Dept 模型
    __table_args__ = (
        sa.Index('idx_dept_parent_id', 'parent_id'),
        sa.Index('idx_dept_name', 'name'),
    )

    name: str = Field(
        ..., max_length=32, unique=True, description="部门名称")
    code: str = Field(..., max_length=32, unique=True, description="部门编码")
    notes: str | None = Field(
        None, max_length=255, description="备注")
    parent_id: int | None = Field(
        default=None,
        foreign_key="sys_dept.id",
        ondelete='RESTRICT',
        description="父部门ID")
    sort_order: int = Field(default=0, description="排序")


class Dept(DeptBase, TreeModel, table=True):
    """部门表"""
    __tablename__: Literal["sys_dept"] = "sys_dept"

    # Relationships
    users: list["User"] = Relationship(back_populates="dept")
    children: list["Dept"] = Relationship(
        sa_relationship_kwargs={
            "cascade": "all, delete-orphan"
        },
        passive_deletes=True
    )


class DeptCreate(DeptBase):
    """部门创建模型"""


class DeptUpdate(DeptCreate):
    """部门更新模型"""
    id: int


class DeptWithUsers(DeptBase):
    """部门与用户关系模型"""
    id: int
    users: list["User"] = Relationship(back_populates="dept")
