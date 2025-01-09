# src/common/data_model/base_model.py

from datetime import datetime
from typing import Annotated, Any, Type, TypeVar

from sqlmodel import Field, SQLModel
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import declared_attr
import sqlalchemy as sa

from src.database.db_session import AuditAsyncSession, async_session, async_engine
from src.utils.timezone import TimeZone
from src.utils.snowflake import id_worker
from src.core.conf import settings

T = TypeVar('T', bound='DatabaseModel')

if settings.APP_ENV == 'dev':
    id_pk = Annotated[int | None, Field(
        default=None,
        primary_key=True,
        description="主键ID",
        sa_column_kwargs={"autoincrement": True}
    )]
else:
    id_pk = Annotated[int, Field(
        primary_key=True,
        index=True,
        default_factory=id_worker.get_id,
        description='主键ID',
        sa_type=sa.BIGINT,
    )]

class SoftDeleteMixin(SQLModel):
    """软删除混入类"""
    deleted_at: datetime | None = Field(default=None, sa_column_kwargs={"comment": "删除时间"})


class DateTimeMixin(SQLModel):
    """时间戳混入类"""
    created_at: datetime = Field(
        default_factory=TimeZone.now,
        sa_column_kwargs={"comment": "创建时间"}
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": TimeZone.now, "comment": "更新时间"}
    )


class DatabaseModel(AsyncAttrs, DateTimeMixin):
    """数据库模型基类"""
    __abstract__ = True

    class Config:
        from_attributes = True
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True

    @classmethod
    def query_session(cls) -> AuditAsyncSession:
        return async_session()

    def __tablename__(self) -> str:
        return self.__name__.lower()

    async def to_dict(
        self,
        *,
        exclude: list[str] | None = None,
        include: list[str] | None = None,
        max_depth: int = 2,
        _depth: int = 1
    ) -> dict[str, Any]:
        """转换为字典"""
        if _depth > max_depth:
            return {"id": getattr(self, 'id', None)}

        data = self.model_dump(exclude_none=True)
        if include:
            data = {k: v for k, v in data.items() if k in include}
        if exclude:
            data = {k: v for k, v in data.items() if k not in exclude}

        return data

    async def to_api_dict(self, max_depth: int = 2) -> dict[str, Any]:
        """转换为API响应格式的字典"""
        exclude_fields = ['password']
        return await self.to_dict(exclude=exclude_fields, max_depth=max_depth)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={getattr(self, 'id', None)}, name={getattr(self, 'name', None)}, code={getattr(self, 'code', None)}>"


async def create_table() -> None:
    """创建表"""
    from src.database.db_session import async_engine
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
