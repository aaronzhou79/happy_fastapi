import sqlalchemy as sa

from sqlmodel import Field, SQLModel

from src.core.context import get_tenant_id


class TenantMixin(SQLModel):
    """租户混入类"""
    tenant_id: int | None = Field(
        default_factory=get_tenant_id,
        nullable=True,
        index=True,
        sa_type=sa.Integer,
        sa_column_kwargs={"comment": "租户ID"}
    )