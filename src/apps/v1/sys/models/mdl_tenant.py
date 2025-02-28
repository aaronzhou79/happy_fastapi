from enum import StrEnum
from typing import TYPE_CHECKING, Literal

from sqlmodel import Field, Relationship, SQLModel

from src.apps.v1.sys.models.mdl_user_tenant import UserTenant
from src.common.base_models.database_mixin import DatabaseModel

if TYPE_CHECKING:
    from src.apps.v1.sys.models.mdl_user import User


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
    users: list['User'] = Relationship(back_populates="tenants", link_model=UserTenant)


class TenantCreate(TenantBase):
    """账套创建"""


class TenantUpdate(TenantBase):
    """账套更新"""
    id: int = Field(..., description="账套ID")


class TenantGet(TenantBase):
    """数据获取模型"""
    id: int = Field(..., description="账套ID")