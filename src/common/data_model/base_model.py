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

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Literal, Optional, Sequence, Tuple, Type, TypeVar

import sqlalchemy as sa

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.core.conf import settings
from src.database.db_session import (
    AuditAsyncSession,
    async_engine,
    async_session,
)
from src.utils.timezone import TimeZone

from .query_fields import FilterGroup, QueryOptions

T = TypeVar('T', bound='DatabaseModel')


# 审计操作类型
class AuditActionType(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RESTORE = "restore"


@dataclass
class AuditMeta:
    """审计元数据"""
    operator_id: int | None = None
    comment: str | None = None


class AuditConfig:
    """审计配置"""
    enabled: bool = False
    # 需要审计的字段,为空表示全部
    fields: set[str] = set()
    # 需要忽略的字段
    exclude_fields: set[str] = {'created_at', 'updated_at'}

    def __init__(
        self,
        enabled: bool = False,
        fields: set[str] = set(),
        exclude_fields: set[str] = {'created_at', 'updated_at'}
    ):
        self.enabled = enabled
        self.fields = fields
        self.exclude_fields = exclude_fields


class DatabaseModel(AsyncAttrs, DeclarativeBase):
    """
    数据库模型基类，提供基础能力支持
    """
    __abstract__ = True
    _locks: dict[int, asyncio.Lock] = {}  # 用于存储每个实例的锁
    audit_config: AuditConfig = AuditConfig()

    @classmethod
    def query_session(cls):
        """返回数据库会话上下文管理器(类方法)"""
        return async_session()

    @classmethod
    async def _do_audit(
        cls,
        session: AuditAsyncSession,
        action: AuditActionType,
        instance: Optional['DatabaseModel'],
        changes: dict[str, Any] | None = None,
        meta: AuditMeta | None = None
    ) -> None:
        """执行审计"""
        if not cls.audit_config.enabled:
            return

        # 获取审计字段
        audit_fields = cls.audit_config.fields or set(cls.get_columns()) - cls.audit_config.exclude_fields

        # 过滤审计数据
        def filter_data(data: dict) -> dict:
            filtered = {}
            # 处理普通字段
            for k, v in data.items():
                if k in audit_fields:
                    filtered[k] = v
            return filtered

        # 处理关系数据的变更
        def process_relationship_changes(data: dict) -> dict:
            relationship_changes = {}
            for rel_name, rel in cls.get_relationships().items():
                if rel_name not in data:
                    continue

                rel_data = data[rel_name]
                if not rel_data:
                    continue

                # 获取关联模型类
                related_model = rel.mapper.class_

                if rel.uselist:  # 一对多关系
                    changes_list = []
                    for item in rel_data:
                        item_id = item.get('id')
                        if item_id:
                            # 更新或删除操作
                            changes_list.append({
                                'id': item_id,
                                'action': 'update' if not item.get('deleted_at') else 'delete',
                                'changes': filter_data(item)
                            })
                        else:
                            # 新增操作
                            changes_list.append({
                                'action': 'create',
                                'changes': filter_data(item)
                            })
                    relationship_changes[rel_name] = changes_list
                else:  # 一对一关系
                    if isinstance(rel_data, dict):
                        relationship_changes[rel_name] = {
                            'action': 'update' if rel_data.get('id') else 'create',
                            'changes': filter_data(rel_data)
                        }

            return relationship_changes

        # 构建审计记录
        audit_log = {
            'action': action.value,
            'target_type': cls.__name__,
            'target_id': instance.id if instance else None,
            'changes': {
                'before': filter_data(instance._dict) if instance else None,
                'after': filter_data(changes) if changes else None,
                'relationships': process_relationship_changes(changes) if changes else None
            },
            'operator_id': meta.operator_id if meta else None,
            'comment': meta.comment if meta else None,
            'created_at': TimeZone.now()
        }

        # 保存审计日志
        await AuditLog.create(session, **audit_log)


    @property
    def lock(self) -> asyncio.Lock:
        """获取实例的同步锁"""
        if self.primary_key_value not in self._locks:
            self._locks[self.primary_key_value] = asyncio.Lock()
        return self._locks[self.primary_key_value]

    async def with_lock(self, callback) -> Any:
        """使用同步锁执行操作"""
        async with self.lock:
            return await callback()

    @classmethod
    def release_lock(cls, id: int) -> None:
        """释放指定ID的锁"""
        if id in cls._locks:
            del cls._locks[id]

    # 使用类名小写作为表名
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    # 基础字段
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True, comment="主键ID")
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False, default=TimeZone.now(), comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, default=TimeZone.now(), onupdate=TimeZone.now(), comment="更新时间"
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
                    else:
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
            if rel_data is None:
                continue

            # 获取关联模型类
            related_model = rel.mapper.class_

            # 获取外键字段名
            foreign_key = None
            for pair in rel.local_remote_pairs:
                if pair[0].name in cls.get_columns():
                    foreign_key = pair[1].name
                    break

            if rel.uselist:  # 一对多关系
                # 获取现有关系数据
                existing_items = await getattr(instance.awaitable_attrs, rel_name)
                existing_map = {item.id: item for item in existing_items}

                # 处理新的关系数据
                new_items = []
                for item_data in rel_data:
                    item_id = item_data.get('id')
                    if item_id:
                        # 检查记录是否存在
                        stmt = select(related_model).where(related_model.id == item_id)
                        result = await session.execute(stmt)
                        item = result.scalar_one_or_none()

                        if item:
                            # 更新现有数据
                            for key, value in item_data.items():
                                if hasattr(item, key):
                                    setattr(item, key, value)
                            # 确保外键值正确
                            if foreign_key:
                                setattr(item, foreign_key, instance.id)
                            new_items.append(item)
                            if item.id in existing_map:
                                del existing_map[item.id]
                        else:
                            # ID不存在，创建新数据
                            new_item = related_model()
                            for key, value in item_data.items():
                                if hasattr(new_item, key):
                                    setattr(new_item, key, value)
                            # 设置外键值
                            if foreign_key:
                                setattr(new_item, foreign_key, instance.id)
                            new_items.append(new_item)
                    else:
                        # 创建新数据
                        new_item = related_model()
                        for key, value in item_data.items():
                            if hasattr(new_item, key):
                                setattr(new_item, key, value)
                        # 设置外键值
                        if foreign_key:
                            setattr(new_item, foreign_key, instance.id)
                        new_items.append(new_item)

                # 处理不再存在的数据
                for item in existing_map.values():
                    if hasattr(item, 'deleted_at'):
                        # 软删除时只设置deleted_at，保持其他字段不变
                        setattr(item, 'deleted_at', TimeZone.now())
                        new_items.append(item)  # 保留在关系中
                    else:
                        # 硬删除
                        await session.delete(item)

                # 更新关系
                setattr(instance, rel_name, new_items)
            else:  # 一对一/多对一关系
                if isinstance(rel_data, dict):
                    related_instance = await getattr(instance.awaitable_attrs, rel_name)
                    if related_instance:
                        # 更新现有数据
                        for key, value in rel_data.items():
                            if hasattr(related_instance, key):
                                setattr(related_instance, key, value)
                        # 确保外键值正确
                        if foreign_key:
                            setattr(related_instance, foreign_key, instance.id)
                    else:
                        # 创建新数据
                        related_instance = related_model(**rel_data)
                        # 设置外键值
                        if foreign_key:
                            setattr(related_instance, foreign_key, instance.id)
                        setattr(instance, rel_name, related_instance)

    @classmethod
    async def create(cls: type[T], session: AuditAsyncSession, **kwargs) -> dict:
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

        # 记录审计
        await cls._do_audit(
            session,
            AuditActionType.CREATE,
            instance,
            kwargs,
            AuditMeta(operator_id=session.user_id)
        )

        return await instance.to_api_dict()

    @classmethod
    async def update(cls: type[T], session: AuditAsyncSession, pk: int, **kwargs) -> dict:
        """更新记录(支持关系数据)"""
        if not pk:
            raise ValueError("主键ID不能为空")

        # 查询实例
        stmt = select(cls).where(cls.id == pk)
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

        # 记录审计
        await cls._do_audit(
            session,
            AuditActionType.UPDATE,
            instance,
            kwargs,
            AuditMeta(operator_id=session.user_id)
        )

        await session.flush()
        return await instance.to_api_dict()

    @classmethod
    async def delete(cls: type[T], session: AuditAsyncSession, pk: int) -> None:
        """删除（带锁保护）"""
        if not pk:
            raise ValueError("主键ID不能为空")

        # 在同一会话中查询实例
        stmt = select(cls).where(cls.id == pk)
        result = await session.execute(stmt)
        instance = result.scalar_one_or_none()

        if instance is None:
            raise ValueError("记录不存在")

        # 记录审计
        await cls._do_audit(
            session,
            AuditActionType.DELETE,
            instance,
            None,
            AuditMeta(operator_id=session.user_id)
        )

        if hasattr(instance, 'deleted_at'):
            if getattr(instance, 'deleted_at') is not None:
                raise ValueError("记录已被逻辑删除，不能再次操作删除！")
            setattr(instance, 'deleted_at', TimeZone.now())
        else:
            await session.delete(instance)

        await session.flush()

    @classmethod
    async def restore(cls: type[T], pk: int, session: AuditAsyncSession) -> None:
        """恢复"""
        if not pk:
            raise ValueError("主键ID不能为空")

        stmt = select(cls).where(cls.id == pk)
        result = await session.execute(stmt)
        instance = result.scalar_one_or_none()

        if instance is None:
            raise ValueError("记录不存在")

        # 记录审计
        await cls._do_audit(
            session,
            AuditActionType.RESTORE,
            instance,
            {'deleted_at': None},
            AuditMeta(operator_id=session.user_id)
        )

        setattr(instance, 'deleted_at', None)
        await session.flush()

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
    async def get_by_id(cls: type[T], id: int) -> T | None:
        """通过ID获取记录"""
        stmt = sa.select(cls).where(cls.id == id)
        result = await cls.query_session().execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(
        cls: type[T],
        *,
        include_deleted: bool = False,
        offset: int = 0,
        limit: int = 100
    ) -> list[T]:
        """获取所有记录，支持分页"""
        stmt = sa.select(cls).offset(offset).limit(limit)
        if hasattr(cls, 'deleted_at') and not include_deleted:
            stmt = stmt.where(getattr(cls, 'deleted_at').is_(None))
        result = await cls.query_session().execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def bulk_create(
        cls: type[T],
        session: AsyncSession,
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
        try:
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
        finally:
            for id in ids:
                cls.release_lock(id)

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
        options: QueryOptions | None = None,
        return_dict: bool = True
    ) -> Sequence[T] | Sequence[dict]:
        """
        通用查询方法
        """
        items, _ = await cls.query_with_count(options=options, return_dict=return_dict)
        return items

    @classmethod
    async def query_with_count(
        cls: type[T],
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
            return await cls._query_with_count_window(options, return_dict)
        else:
            return await cls._query_with_count_basic(options, return_dict)

    @classmethod
    async def _query_with_count_window(
        cls: type[T],
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
        result = await cls.query_session().execute(query)
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

        items = await cls.query_session().scalars(query)
        items = items.all()
        total = await cls.query_session().scalar(count_query) or 0

        if return_dict and items:
            items = [await item.to_dict() for item in items]

        return items, total

    @classmethod
    async def count(
        cls: type[T],
        filters: FilterGroup | None = None
    ) -> int:
        """
        获取记录总数
        """
        stmt = select(func.count()).select_from(cls)
        if filters:
            stmt = stmt.where(filters.build_query(cls))
        return await cls.query_session().scalar(stmt) or 0

    @classmethod
    async def exists(
        cls: type[T],
        filters: FilterGroup | None = None
    ) -> bool:
        """
        检查记录是否存在
        """
        return await cls.count(filters) > 0

    @classmethod
    def filter_attrs(cls, data: dict[str, Any]) -> dict[str, Any]:
        """过滤掉不存在的属性"""
        return {k: v for k, v in data.items() if hasattr(cls, k)}

    async def to_dict(
        self,
        exclude: list[str] | None = None,
        include: list[str] | None = None,
        _parent_type: type | None = None,
        max_depth: int = 2,
        _depth: int = 1
    ) -> dict[str, Any]:
        # 如果超过最大深度,直接返回 ID
        if _depth > max_depth:
            return {"id": self.id}

        data = self._dict
        if include:
            data = {k: v for k, v in data.items() if k in include}
        if exclude:
            data = {k: v for k, v in data.items() if k not in exclude}

        # 如果已达到最大深度,跳过关系对象处理
        if _depth == max_depth:
            return data

        # 处理关系对象
        for rel_name, rel in self.get_relationships().items():
            if include and rel_name not in include:
                continue
            if exclude and rel_name in exclude:
                continue

            # 跳过父级类型的关系
            if _parent_type and rel.mapper.class_ == _parent_type:
                continue

            value = await getattr(self.awaitable_attrs, rel_name)
            if value is not None:
                if hasattr(value, 'to_dict'):
                    data[rel_name] = await value.to_dict(
                        exclude=exclude,
                        include=include,
                        _parent_type=self.__class__,
                        max_depth=max_depth,
                        _depth=_depth + 1
                    )
                elif isinstance(value, list):
                    data[rel_name] = [
                        await item.to_dict(
                            exclude=exclude,
                            include=include,
                            _parent_type=self.__class__,
                            max_depth=max_depth,
                            _depth=_depth + 1
                        ) if hasattr(item, 'to_dict') else item
                        for item in value
                    ]

        return data

    async def to_api_dict(self, max_depth: int = 2) -> dict[str, Any]:
        """
        转换为API响应格式的字典
        默认排除一些敏感或内部字段
        """
        exclude_fields = ['password']
        return await self.to_dict(exclude=exclude_fields, max_depth=max_depth)


class SoftDeleteMixin:
    """
    软删除混入类
    """
    __abstract__ = True

    deleted_at: Mapped[datetime | None] = mapped_column(sa.DateTime, nullable=True, comment="删除时间")


class TimestampMixin:
    """
    时间戳混入类
    """
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, default=TimeZone.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, default=TimeZone.now(), onupdate=TimeZone.now(), comment="更新时间"
    )

    def touch(self) -> None:
        """更新更新时间"""
        self.updated_at = TimeZone.now()


class AuditLog(DatabaseModel):
    """审计日志表"""
    __tablename__: Literal['sys_audit_logs'] = 'sys_audit_logs'
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True, comment="ID")
    target_type: Mapped[str] = mapped_column(sa.String(50), nullable=False, comment="目标类型")
    target_id: Mapped[int] = mapped_column(sa.Integer, nullable=False, comment="目标ID")
    action: Mapped[str] = mapped_column(sa.String(20), nullable=False, comment="操作类型")
    changes: Mapped[dict] = mapped_column(sa.JSON, nullable=False, comment="变更内容")
    operator_id: Mapped[int] = mapped_column(sa.Integer, nullable=True, comment="操作人ID")
    comment: Mapped[str] = mapped_column(sa.String(500), nullable=True, comment="备注")


async def create_table():
    """创建数据库表"""
    async with async_engine.begin() as conn:
        await conn.run_sync(DatabaseModel.metadata.create_all)