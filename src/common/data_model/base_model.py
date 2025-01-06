# src/common/data_model/base_model.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : base_model.py
# @Software: Cursor
# @Description: 数据库模型基类，提供基础能力支持
"""
数据库模型基类，提供基础能力支持
"""
import asyncio

from datetime import datetime
from typing import Any, Awaitable, Callable, Sequence, Tuple, Type, TypeVar

import sqlalchemy as sa

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, RelationshipProperty, mapped_column, registry

from src.core.conf import settings
from src.database.db_session import (
    AuditAsyncSession,
    async_engine,
    async_session,
)
from src.utils.timezone import TimeZone

from .query_fields import FilterGroup, QueryOptions

T = TypeVar('T', bound='DatabaseModel')

mapper_registry = registry()


class Base(AsyncAttrs, DeclarativeBase):
    """
    基础模型类
    """
    registry = mapper_registry


class SoftDeleteMixin(Base):
    """
    软删除混入类
    """
    __abstract__ = True

    deleted_at: Mapped[datetime | None] = mapped_column(sa.DateTime, nullable=True, comment="删除时间")


class DateTimeMixin(Base):
    """
    时间戳混入类
    """
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, default=TimeZone.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime, nullable=True, onupdate=TimeZone.now(), comment="更新时间"
    )


class DatabaseModel(Base):
    """
    数据库模型基类，提供基础能力支持
    """
    __abstract__ = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 将_locks移到实例初始化中
        if not hasattr(self, '_locks'):
            self._locks = {}

    @classmethod
    def query_session(cls) -> AuditAsyncSession:
        """返回数据库会话上下文管理器(类方法)"""
        return async_session()

    @property
    def lock(self) -> asyncio.Lock:
        """获取实例的同步锁"""
        if self.primary_key_value not in self._locks:
            self._locks[self.primary_key_value] = asyncio.Lock()
        return self._locks[self.primary_key_value]

    async def with_lock(self, callback: Callable[[], Awaitable[Any]]) -> Any:
        """使用同步锁执行操作"""
        async with self.lock:
            return await callback()

    def release_lock(self) -> None:
        """释放指定ID的锁"""
        if self.primary_key_value in self._locks:
            del self._locks[self.primary_key_value]

    # 使用类名小写作为表名
    @declared_attr.directive
    def __tablename__(self) -> str:
        """设置/获取表名"""
        return self.__name__.lower()

    # 基础字段
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
        # 处理datetime类型
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
    async def _check_unique_constraints(
        cls,
        session: AsyncSession,
        model: Type[Any],
        data: dict[str, Any]
    ) -> tuple[bool, Any]:
        """检查唯一约束

        Returns:
            tuple[bool, Any]: (是否找到软删除的记录, 找到的记录)
        """
        # 获取模型的唯一约束
        unique_constraints = []
        for constraint in model.__table__.constraints:
            if isinstance(constraint, sa.UniqueConstraint):
                unique_constraints.extend(constraint.columns)

        # 检查每个唯一约束字段
        for column in unique_constraints:
            field_name = column.name
            if field_name in data:
                value = data[field_name]
                # 构建查询（包括软删除的记录）
                stmt = select(model).where(
                    getattr(model, field_name) == value
                )
                result = await session.execute(stmt)
                existing_record = result.scalar_one_or_none()

                if existing_record:
                    # 如果记录存在但已软删除，返回该记录
                    if hasattr(existing_record, 'deleted_at') and existing_record.deleted_at is not None:
                        return True, existing_record
                    # 如果记录存在且未软删除，抛出错误
                    raise ValueError(f"字段 '{field_name}' 的值 '{value}' 已存在")

        return False, None

    @classmethod
    async def _handle_relationships(
        cls,
        session: AsyncSession,
        instance: 'DatabaseModel',
        data: dict[str, Any]
    ) -> None:
        """处理关系数据的创建和更新"""
        for rel_name, rel in cls.get_relationships().items():
            if rel_name not in data:
                continue

            rel_data = data[rel_name]
            related_model = rel.mapper.class_
            foreign_key = cls._get_foreign_key(rel)
            if foreign_key is None:
                continue

            if rel.uselist:  # 一对多关系
                await cls._handle_one_to_many_relationship(
                    session, instance, rel_name, rel_data, related_model, foreign_key
                )

    @classmethod
    async def _handle_one_to_many_relationship(
        cls,
        session: AsyncSession,
        instance: 'DatabaseModel',
        rel_name: str,
        rel_data: list[dict[str, Any]] | None,
        related_model: Type['DatabaseModel'],
        foreign_key: str
    ) -> None:
        """处理一对多关系"""
        existing_items = await getattr(instance.awaitable_attrs, rel_name)
        existing_map = {item.id: item for item in existing_items}
        new_items = []

        if rel_data is not None:
            for item_data in rel_data:
                item_id = item_data.get('id')
                if item_id:
                    item = await cls._get_or_create_related_instance(
                        session, related_model, item_id, item_data
                    )
                    if item:
                        cls._update_instance(item, item_data)
                        if foreign_key:
                            setattr(item, foreign_key, instance.id)
                        new_items.append(item)
                        if item.id in existing_map:
                            del existing_map[item.id]
                else:
                    item = cls._create_related_instance(related_model, item_data)
                    if foreign_key:
                        setattr(item, foreign_key, instance.id)
                    new_items.append(item)

        await cls._handle_removed_items(session, list(existing_map.values()))
        setattr(instance, rel_name, new_items)

    @classmethod
    def _get_foreign_key(cls, rel: RelationshipProperty) -> str | None:
        """获取外键字段名"""
        if rel.local_remote_pairs is None:
            return None
        for pair in rel.local_remote_pairs:
            if pair[0].name in cls.get_columns():
                return pair[1].name
        return None

    @classmethod
    async def _get_or_create_related_instance(
        cls,
        session: AsyncSession,
        related_model: Type['DatabaseModel'],
        item_id: Any,
        item_data: dict[str, Any]
    ) -> 'DatabaseModel':
        """获取或创建关联实例"""
        stmt = select(related_model).where(related_model.id == item_id)
        result = await session.execute(stmt)
        item = result.scalar_one_or_none()
        if not item:
            item = cls._create_related_instance(related_model, item_data)
        return item

    @classmethod
    def _create_related_instance(
        cls,
        related_model: Type['DatabaseModel'],
        item_data: dict[str, Any]
    ) -> 'DatabaseModel':
        """创建关联实例"""
        return related_model(**item_data)

    @classmethod
    def _update_instance(
        cls,
        instance: 'DatabaseModel',
        data: dict[str, Any]
    ) -> None:
        """更新实例字段"""
        for key, value in data.items():
            if hasattr(instance, key) and value is not None:  # 只更新非 None 值
                setattr(instance, key, value)

    @classmethod
    async def _handle_removed_items(
        cls,
        session: AsyncSession,
        items: list['DatabaseModel']
    ) -> None:
        """处理不再存在的数据（软删除或硬删除）"""
        for item in items:
            if hasattr(item, 'deleted_at'):
                setattr(item, 'deleted_at', TimeZone.now())
                await session.merge(item)  # 保留在关系中
            else:
                await session.delete(item)  # 硬删除

    @classmethod
    async def create(cls: type[T], session: AuditAsyncSession, **kwargs: Any) -> dict:
        """创建记录(支持关系数据)"""
        # 分离关系数据
        relationship_data = {}
        model_data = {}
        for key, value in kwargs.items():
            if key in cls.get_relationships():
                relationship_data[key] = value
            else:
                model_data[key] = value

        # 创建主表记录
        instance = cls(**model_data)
        session.add(instance)
        await session.flush()

        # 处理关系数据
        await cls._handle_relationships(session, instance, relationship_data)
        await session.flush()

        return await instance.to_api_dict()

    @classmethod
    async def update(cls: type[T], session: AuditAsyncSession, **kwargs: Any) -> dict:
        """更新记录(支持关系数据)"""
        primary_key_name = cls.get_primary_key()
        if primary_key_name not in kwargs:
            raise ValueError(f"没有配置主键{primary_key_name}！")
        pk = kwargs.pop(primary_key_name)
        if not pk:
            raise ValueError(f"主键{primary_key_name}不能为空！")

        # 查询实例
        stmt = select(cls).where(getattr(cls, primary_key_name) == pk)
        result = await session.execute(stmt)
        instance = result.scalar_one_or_none()

        if instance is None:
            raise ValueError("记录不存在")

        # 分离关系数据
        relationship_data = {}
        model_data = {}
        for key, value in kwargs.items():
            if key in cls.get_relationships():
                relationship_data[key] = value
            elif hasattr(instance, key):
                model_data[key] = value

        # 更新主表数据
        for key, value in model_data.items():
            setattr(instance, key, value)

        # 处理关系数据
        await cls._handle_relationships(session, instance, relationship_data)

        await session.flush()
        return await instance.to_api_dict()

    async def update_fields(self, session: AuditAsyncSession, **kwargs: Any) -> None:
        """更新字段"""
        for key, value in kwargs.items():
            setattr(self, key, value)
        await session.flush()

    @classmethod
    async def delete(cls: type[T], session: AuditAsyncSession, **kwargs: Any) -> None:
        """删除（带锁保护）"""
        primary_key_name = cls.get_primary_key()
        if primary_key_name not in kwargs:
            raise ValueError(f"没有配置主键{primary_key_name}！")
        pk = kwargs.pop(primary_key_name)
        if not pk:
            raise ValueError(f"主键{primary_key_name}不能为空！")

        # 在同一会话中查询实例
        stmt = select(cls).where(getattr(cls, primary_key_name) == pk)
        result = await session.execute(stmt)
        instance = result.scalar_one_or_none()

        if instance is None:
            raise ValueError("记录不存在")

        if hasattr(instance, 'deleted_at'):
            if getattr(instance, 'deleted_at') is not None:
                raise ValueError("记录已被逻辑删除，不能再次操作删除！")
            setattr(instance, 'deleted_at', TimeZone.now())
        else:
            await session.delete(instance)

        await session.flush()

    @classmethod
    async def restore(cls: type[T], session: AuditAsyncSession, **kwargs: Any) -> None:
        """恢复"""
        primary_key_name = cls.get_primary_key()
        if primary_key_name not in kwargs:
            raise ValueError(f"没有配置主键{primary_key_name}！")
        pk = kwargs.pop(primary_key_name)
        if not pk:
            raise ValueError(f"主键{primary_key_name}不能为空！")

        stmt = select(cls).where(getattr(cls, primary_key_name) == pk)
        result = await session.execute(stmt)
        instance = result.scalar_one_or_none()

        if instance is None:
            raise ValueError("记录不存在")

        if hasattr(instance, 'deleted_at'):
            setattr(instance, 'deleted_at', None)
        else:
            raise ValueError("记录未被软删除")

        await session.flush()

    @classmethod
    def get_primary_key(cls) -> str:
        """获取主键字段名"""
        return cls.__mapper__.primary_key[0].name

    @property
    def primary_key_value(self) -> Any:
        """获取主键值"""
        return getattr(self, self.__mapper__.primary_key[0].name)

    @property
    def is_deleted(self) -> bool:
        """是否已删除"""
        return getattr(self, 'deleted_at', None) is not None

    def __repr__(self) -> str:
        """模型的字符串表示"""
        return f"<{self.__class__.__name__}(id={self.primary_key_value})>"

    @classmethod
    async def get_by_id(cls: type[T], session: AuditAsyncSession, **kwargs: Any) -> T | None:
        """通过ID获取记录"""
        primary_key_name = cls.get_primary_key()
        if primary_key_name not in kwargs:
            raise ValueError(f"没有配置主键{primary_key_name}！")
        pk = kwargs.pop(primary_key_name)
        if not pk:
            raise ValueError(f"主键{primary_key_name}不能为空！")

        stmt = select(cls).where(getattr(cls, primary_key_name) == pk)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_fields(cls: type[T], session: AuditAsyncSession, **kwargs: Any) -> T | None:
        """通过字段获取记录"""
        stmt = select(cls).where(*[getattr(cls, k) == v for k, v in kwargs.items()])
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(
        cls: type[T],
        *,
        session: AuditAsyncSession,
        include_deleted: bool = False,
        offset: int = 0,
        limit: int = 100
    ) -> list[T]:
        """获取所有记录，支持分页"""
        stmt = sa.select(cls).offset(offset).limit(limit)
        if hasattr(cls, 'deleted_at') and not include_deleted:
            stmt = stmt.where(getattr(cls, 'deleted_at').is_(None))
        result = await session.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def bulk_create(
        cls: type[T],
        session: AuditAsyncSession,
        items: list[dict[str, Any]],
        return_instances: bool = True
    ) -> list[T] | None:
        """批量创建记录"""
        instances = [cls(**item) for item in items]
        session.add_all(instances)
        await session.flush()
        return instances if return_instances else None

    @classmethod
    async def bulk_update(
        cls: type[T],
        session: AsyncSession,
        items: list[tuple[int, dict[str, Any]]],
        return_instances: bool = True
    ) -> list[T] | None:
        """批量更新记录"""
        # 获取所有ID
        ids = [item[0] for item in items]
        # 构建更新映射
        update_map = {item[0]: item[1] for item in items}

        # 获取所有实例
        stmt = sa.select(cls).where(cls.id.in_(ids))
        result = await session.execute(stmt)
        instances = list(result.scalars().all())

        # 更新实例
        for instance in instances:
            if instance.id in update_map:
                for key, value in update_map[instance.id].items():
                    setattr(instance, key, value)

        await session.flush()

        return instances if return_instances else None

    @classmethod
    async def bulk_delete(
        cls: type[T],
        session: AsyncSession,
        ids: list[int],
        soft_delete: bool = True
    ) -> None:
        """批量删除记录"""
        if soft_delete and hasattr(cls, 'deleted_at'):
            stmt = (
                sa.update(cls)
                .where(cls.id.in_(ids))
                .values(deleted_at=TimeZone.now())
            )
        else:
            stmt = sa.delete(cls).where(cls.id.in_(ids))

        await session.execute(stmt)
        await session.flush()

    @classmethod
    async def bulk_restore(
        cls: type[T],
        session: AsyncSession,
        ids: list[int],
        return_instances: bool = True
    ) -> list[T] | None:
        """批量恢复记录"""
        if not hasattr(cls, 'deleted_at'):
            raise AttributeError(f"{cls.__name__} 不支持软删除")

        stmt = (
            sa.update(cls)
            .where(cls.id.in_(ids))
            .values(deleted_at=None)
        )
        await session.execute(stmt)
        await session.flush()

        if return_instances:
            stmt = sa.select(cls).where(cls.id.in_(ids))
            result = await session.execute(stmt)
            return list(result.scalars().all())
        return None

    @classmethod
    async def query(
        cls: type[T],
        session: AuditAsyncSession,
        options: QueryOptions | None = None,
        return_dict: bool = True
    ) -> Sequence[T] | Sequence[dict]:
        """
        通用查询方法
        """
        items, _ = await cls.query_with_count(session=session, options=options, return_dict=return_dict)
        return items

    @classmethod
    async def query_with_count(
        cls: type[T],
        session: AuditAsyncSession,
        options: QueryOptions | None = None,
        return_dict: bool = True
    ) -> Tuple[Sequence[T] | Sequence[dict], int]:
        """带总数的通用查询方法"""
        options = options or QueryOptions()

        # 获取数据库类型
        db_type = settings.DB_TYPE
        features = settings.DB_FEATURES.get(db_type, {})

        # 根据数据库特性选择查询策略
        if features.get('supports_window_functions'):
            return await cls._query_with_count_window(session, options, return_dict)
        return await cls._query_with_count_basic(session, options, return_dict)

    @classmethod
    async def _query_with_count_window(
        cls: type[T],
        session: AuditAsyncSession,
        options: QueryOptions,
        return_dict: bool
    ) -> Tuple[Sequence[T] | Sequence[dict], int]:
        """使用窗口函数的查询实现"""
        options = options or QueryOptions()

        # 构建基础查询
        base_query = select(
            cls,
            func.count().over().label('total_count')
        )

        if options.filters and options.filters:
            base_query = base_query.where(options.filters.build_query(cls))

        # 添加排序和分页
        query = base_query.order_by(*(
            getattr(cls, sort_field.field).desc()
            if sort_field.order.value == "desc"
            else getattr(cls, sort_field.field).asc()
            for sort_field in (options.sort or [])
        )).offset(options.offset).limit(options.limit)

        # 执行查询
        result = await session.execute(query)
        rows = result.all()

        if not rows:
            return [], 0

        # 从第一行获取总数
        total = rows[0].total_count

        # 提取实体对象
        items = [row[0] for row in rows]

        # 如果需要返回字典
        if return_dict:
            items = [await instance.to_dict() for instance in items]

        return items, total

    @classmethod
    async def _query_with_count_basic(
        cls: type[T],
        session: AuditAsyncSession,
        options: QueryOptions,
        return_dict: bool
    ) -> Tuple[Sequence[T] | Sequence[dict], int]:
        """基础查询实现"""
        where_clause = options.filters.build_query(cls) if options.filters else None

        # 分别执行数据查询和计数查询
        query = select(cls)
        if where_clause is not None:
            query = query.where(where_clause)
        if options.sort:
            query = query.order_by(*(
                getattr(cls, sort_field.field).desc()
                if sort_field.order.value == "desc"
                else getattr(cls, sort_field.field).asc()
                for sort_field in options.sort
            ))
        query = query.offset(options.offset).limit(options.limit)

        count_query = select(func.count()).select_from(cls)
        if where_clause is not None:
            count_query = count_query.where(where_clause)

        items = await session.scalars(query)
        items = items.all()
        total = await session.scalar(count_query) or 0

        if return_dict and items:
            items = [await item.to_dict() for item in items]

        return items, total

    @classmethod
    async def count(
        cls: type[T],
        session: AuditAsyncSession,
        filters: FilterGroup | None = None
    ) -> int:
        """
        获取记录总数
        """
        stmt = select(func.count()).select_from(cls)
        if filters:
            stmt = stmt.where(filters.build_query(cls))
        return await session.scalar(stmt) or 0

    @classmethod
    async def exists(
        cls: type[T],
        session: AuditAsyncSession,
        filters: FilterGroup | None = None
    ) -> bool:
        """
        检查记录是否存在
        """
        return await cls.count(session, filters) > 0

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
        """
        转换为API响应格式的字典

        默认排除一些敏感或内部字段
        """
        exclude_fields = ['password']
        return await self.to_dict(exclude=exclude_fields, max_depth=max_depth)


async def create_table() -> None:
    """创建数据库表"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
