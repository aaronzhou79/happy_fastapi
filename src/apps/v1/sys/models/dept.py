from typing import TYPE_CHECKING, Literal

from sqlmodel import Field, Relationship, SQLModel
from sqlmodel.main import SQLModelMetaclass

from src.common.base_model import DatabaseModel, id_pk
from src.common.decorators import optional_fields

if TYPE_CHECKING:
    from src.apps.v1.sys.models.user import User


class DeptBase(SQLModel):
    """部门基础模型"""
    __tablename__: Literal["sys_dept"] = "sys_dept"

    name: str = Field(
        ..., max_length=32, unique=True, description="部门名称")
    code: str = Field(..., max_length=32, unique=True, description="部门编码")
    notes: str | None = Field(
        None, max_length=255, description="备注")


class Dept(DeptBase, DatabaseModel, table=True):
    """部门表"""
    __tablename__: Literal["sys_dept"] = "sys_dept"
    id: id_pk  # type: ignore

    # Relationships
    users: list["User"] = Relationship(back_populates="dept")


class DeptCreate(DeptBase):
    """部门创建模型"""


class DeptUpdate(DeptBase):
    """部门更新模型"""
    id: int


class DeptWithUsers(DeptBase):
    """部门与用户关系模型"""
    id: int
    users: list["User"] = Relationship(back_populates="dept")
