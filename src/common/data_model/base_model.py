# src/common/data_model/base_model.py

from datetime import datetime
from typing import Any, TypeVar

import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, registry

from src.database.db_session import (
    AuditAsyncSession,
    async_engine,
    async_session,
)
from src.utils.timezone import TimeZone

T = TypeVar('T', bound='DatabaseModel')

mapper_registry = registry()


class Base(AsyncAttrs, DeclarativeBase):
    """基础模型类"""
    registry = mapper_registry


class SoftDeleteMixin(Base):
    """软删除混入类"""
    __abstract__ = True

    deleted_at: Mapped[datetime | None] = mapped_column(sa.DateTime, nullable=True, comment="删除时间")


class DateTimeMixin(Base):
    """时间戳混入类"""
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, default=TimeZone.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime, nullable=True, onupdate=TimeZone.now(), comment="更新时间"
    )


class DatabaseModel(Base):
    """数据库模型基类,提供基础能力支持"""
    __abstract__ = True

    @classmethod
    def query_session(cls) -> AuditAsyncSession:
        """返回数据库会话上下文管理器(类方法)"""
        return async_session()

    @declared_attr.directive
    def __tablename__(self) -> str:
        """设置/获取表名"""
        return self.__name__.lower()

    id: Mapped[int] = mapped_column(
        sa.Integer,
        primary_key=True,
        autoincrement=True,
        sort_order=1,
        comment="主键ID",
    )

    @property
    def _dict(self) -> dict[str, Any]:
        """将模型转换为字典"""
        return {c.key: getattr(self, c.key) for c in sa.inspect(self).mapper.column_attrs}

    @property
    def _json(self) -> dict[str, Any]:
        """将模型转换为JSON格式"""
        result = self._dict
        for key, value in result.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
        return result

    @classmethod
    def get_columns(cls) -> list[str]:
        """获取所有列名"""
        return [c.key for c in sa.inspect(cls).mapper.column_attrs]

    @classmethod
    def get_relationships(cls) -> dict[str, Any]:
        """获取所有关系"""
        return {rel.key: rel for rel in sa.inspect(cls).mapper.relationships}

    @classmethod
    def get_primary_key(cls) -> str:
        """获取主键字段名"""
        return cls.__mapper__.primary_key[0].name

    @property
    def is_deleted(self) -> bool:
        """是否已删除"""
        return getattr(self, 'deleted_at', None) is not None

    def __repr__(self) -> str:
        """模型的字符串表示"""
        if hasattr(self, 'name') and hasattr(self, 'code'):
            return f"<{self.__class__.__name__}(id={getattr(self, 'id')}, name={getattr(self, 'name')}, code={getattr(self, 'code')})>"
        if hasattr(self, 'name'):
            return f"<{self.__class__.__name__}(id={getattr(self, 'id')}, name={getattr(self, 'name')})>"
        if hasattr(self, 'code'):
            return f"<{self.__class__.__name__}(id={getattr(self, 'id')}, code={getattr(self, 'code')})>"
        return f"<{self.__class__.__name__}(id={getattr(self, 'id')})>"

    @classmethod
    def filter_attrs(cls, data: dict[str, Any]) -> dict[str, Any]:
        """过滤掉不存在的属性"""
        return {k: v for k, v in data.items() if hasattr(cls, k)}

    async def _process_relationship(
        self,
        rel_name: str,
        exclude: list[str] | None,
        include: list[str] | None,
        max_depth: int,
        _depth: int,
    ) -> dict[str, Any] | list[dict[str, Any]] | None:
        """处理关系对象的转换"""
        value = await getattr(self.awaitable_attrs, rel_name)
        if value is None:
            return None

        if hasattr(value, 'to_dict'):
            return await value.to_dict(
                exclude=exclude,
                include=include,
                _parent_type=self.__class__,
                max_depth=max_depth,
                _depth=_depth + 1
            )
        if isinstance(value, list):
            return [
                await item.to_dict(
                    exclude=exclude,
                    include=include,
                    _parent_type=self.__class__,
                    max_depth=max_depth,
                    _depth=_depth + 1
                ) if hasattr(item, 'to_dict') else item
                for item in value
            ]
        return value

    async def to_dict(
        self,
        *,
        exclude: list[str] | None = None,
        include: list[str] | None = None,
        _parent_type: type | None = None,
        max_depth: int = 2,
        _depth: int = 1
    ) -> dict[str, Any]:
        """转换为字典"""
        if _depth > max_depth:
            return {"id": self.id}

        data = self._dict
        if include:
            data = {k: v for k, v in data.items() if k in include}
        if exclude:
            data = {k: v for k, v in data.items() if k not in exclude}

        if _depth == max_depth:
            return data

        for rel_name, rel in self.get_relationships().items():
            if include and rel_name not in include:
                continue
            if exclude and rel_name in exclude:
                continue
            if _parent_type and rel.mapper.class_ == _parent_type:
                continue

            result = await self._process_relationship(
                rel_name, exclude, include, max_depth, _depth
            )
            if result is not None:
                data[rel_name] = result

        return data

    async def to_api_dict(self, max_depth: int = 2) -> dict[str, Any]:
        """转换为API响应格式的字典"""
        exclude_fields = ['password']
        return await self.to_dict(exclude=exclude_fields, max_depth=max_depth)


async def create_table() -> None:
    """创建数据库表"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
