from datetime import datetime

import sqlalchemy as sa

from sqlmodel import Field, SQLModel

from src.core.user_state import UserState
from src.utils.timezone import TimeZone


class DateTimeMixin(SQLModel):
    """时间戳混入类"""

    created_at: datetime = Field(
        default_factory=TimeZone.now,
        sa_type=sa.TIMESTAMP(timezone=True),  # type: ignore
        sa_column_kwargs={"comment": "创建时间"},
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_type=sa.TIMESTAMP(timezone=True),  # type: ignore
        sa_column_kwargs={"onupdate": TimeZone.now, "comment": "更新时间"},
    )
    created_by: int | None = Field(
        default_factory=UserState.get_current_user_id,
        sa_column_kwargs={"comment": "创建者"},
    )
    updated_by: int | None = Field(
        default=None,
        sa_column_kwargs={
            "onupdate": UserState.get_current_user_id,
            "comment": "更新者",
        },
    )
