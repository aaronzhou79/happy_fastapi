from datetime import datetime

import sqlalchemy as sa

from sqlmodel import Field, SQLModel


class SoftDeleteMixin(SQLModel):
    """软删除混入类"""

    deleted_at: datetime | None = Field(
        default=None,
        sa_type=sa.TIMESTAMP(timezone=True),  # type: ignore
        sa_column_kwargs={"comment": "删除时间"},
    )
