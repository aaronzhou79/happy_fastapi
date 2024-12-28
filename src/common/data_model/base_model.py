from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncGenerator, TypeVar

from sqlalchemy import Column, DateTime, Integer, inspect, select
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

T = TypeVar('T', bound='DatabaseModel')


class DatabaseModel(AsyncAttrs, MappedAsDataclass, DeclarativeBase):
    """
    数据库模型基类，提供基础能力支持
    """

    # 使用类名小写作为表名
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    # 基础字段
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    @property
    def _dict(self) -> dict[str, Any]:
        """将模型转换为字典"""
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

    @property
    def _json(self) -> dict[str, Any]:
        """将模型转换为JSON格式"""
        result = self._dict
        # 处理datetime类型
        for key, value in result.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
        return result

    @classmethod
    def get_columns(cls) -> list[str]:
        """获取所有列名"""
        return [c.key for c in inspect(cls).mapper.column_attrs]

    @classmethod
    def get_relationships(cls) -> dict[str, Any]:
        """获取所有关系"""
        return {rel.key: rel for rel in inspect(cls).mapper.relationships}

    def update(self, **kwargs) -> None:
        """批量更新属性"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @property
    def primary_key_value(self) -> Any:
        """获取主键值"""
        return getattr(self, self.__mapper__.primary_key[0].name)

    def __repr__(self) -> str:
        """模型的字符串表示"""
        return f"<{self.__class__.__name__}(id={self.primary_key_value})>"

    @classmethod
    @asynccontextmanager
    async def transaction(
        cls,
        session: AsyncSession
    ) -> AsyncGenerator[AsyncSession, None]:
        """事务上下文管理器"""
        async with session.begin():
            try:
                yield session
            except Exception:
                await session.rollback()
                raise


    @classmethod
    async def get_by_id(cls: type[T], session: AsyncSession, id: int) -> T | None:
        """通过ID获取记录"""
        stmt = select(cls).where(cls.id == id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(
        cls: type[T],
        session: AsyncSession,
        offset: int = 0,
        limit: int = 100
    ) -> list[T]:
        """获取所有记录，支持分页"""
        stmt = select(cls).offset(offset).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())


class BaseModelMixin(DatabaseModel):
    """
    模型扩展混入类，提供额外的功能
    """

    @classmethod
    def filter_attrs(cls, data: dict[str, Any]) -> dict[str, Any]:
        """过滤掉不存在的属性"""
        return {k: v for k, v in data.items() if hasattr(cls, k)}

    def to_dict(
        self,
        exclude: list[str] | None = None,
        include: list[str] | None = None
    ) -> dict[str, Any]:
        """
        增强的字典转换方法
        :param exclude: 要排除的字段
        :param include: 要包含的字段（如果指定，则只返回这些字段）
        """
        data = self._dict
        if include:
            data = {k: v for k, v in data.items() if k in include}
        if exclude:
            data = {k: v for k, v in data.items() if k not in exclude}

        # 处理关系对象
        for rel_name, rel in self.get_relationships().items():
            if include and rel_name not in include:
                continue
            if exclude and rel_name in exclude:
                continue

            value = getattr(self, rel_name, None)
            if value is not None:
                if hasattr(value, 'to_dict'):
                    data[rel_name] = value.to_dict()
                elif isinstance(value, list):
                    data[rel_name] = [
                        item.to_dict() if hasattr(item, 'to_dict') else item
                        for item in value
                    ]

        return data

    def to_api_dict(self) -> dict[str, Any]:
        """
        转换为API响应格式的字典
        默认排除一些敏感或内部字段
        """
        exclude_fields = ['password', 'deleted_at']
        return self.to_dict(exclude=exclude_fields)


class SoftDeleteMixin:
    """
    软删除混入类
    """
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")

    def soft_delete(self) -> None:
        """软删除"""
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """恢复"""
        self.deleted_at = None

    @property
    def is_deleted(self) -> bool:
        """是否已删除"""
        return self.deleted_at is not None


class TimestampMixin:
    """
    时间戳混入类
    """
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def touch(self) -> None:
        """更新更新时间"""
        self.updated_at = datetime.utcnow()