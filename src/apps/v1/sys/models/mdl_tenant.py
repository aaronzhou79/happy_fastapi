from enum import StrEnum
from typing import Literal

from sqlmodel import Field, SQLModel

from src.common.base_models.database_mixin import DatabaseModel


class TenantStatus(StrEnum):
    """租户状态"""
    ACTIVE = "有效"
    INACTIVE = "无效"


class TenantBase(SQLModel):
    """账套信息基类"""
    name: str = Field(..., description="租户名称")
    code: str = Field(..., description="租户编码")
    notes: str | None = Field(None, description="租户描述")
    status: TenantStatus = Field(default=TenantStatus.ACTIVE, description="租户状态")


class Tenant(TenantBase, DatabaseModel, table=True):
    """账套表"""
    __tablename__: Literal["sys_tenant"] = "sys_tenant"


class TenantCreate(TenantBase):
    """账套创建"""


class TenantUpdate(TenantBase):
    """账套更新"""
    id: int = Field(..., description="账套ID")
