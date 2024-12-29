import asyncio

from datetime import datetime
from typing import Any, Sequence, TypeVar, Tuple

import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.utils.timezone import TimeZone
from src.core.conf import settings

from sqlalchemy import select, func

from .query_fields import QueryOptions, FilterGroup

T = TypeVar('T', bound='DatabaseModel')


class DatabaseModel(AsyncAttrs, DeclarativeBase):
    """
    数据库模型基类，提供基础能力支持
    """
    __abstract__ = True
    query_session: AsyncSession
    _locks: dict[int, asyncio.Lock] = {}  # 用于存储每个实例的锁

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
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False, default=TimeZone.now(), onupdate=TimeZone.now(), comment="更新时间")

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

    async def update(self, **kwargs) -> None:
        """批量更新属性（带锁保护）"""
        try:
            async with self.lock:
                for key, value in kwargs.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                await self.query_session.flush()
                await self.query_session.commit()
        except Exception:
            await self.query_session.rollback()
            raise

    async def delete(self) -> None:
        """删除（带锁保护）"""
        try:
            if hasattr(self, 'deleted_at'):
                if self.deleted_at is not None:
                    raise ValueError("记录已被删除，不能再次操作！")
                self.deleted_at = TimeZone.now()
            else:
                async with self.lock:
                    await self.query_session.delete(self)

            await self.query_session.flush()
            await self.query_session.commit()  # 显式提交事务
        finally:
            self.release_lock(self.primary_key_value)

    async def restore(self) -> None:
        """恢复"""
        try:
            self.deleted_at = None
            await self.query_session.flush()
            await self.query_session.commit()
        except Exception:
            await self.query_session.rollback()
            raise

    @property
    def primary_key_value(self) -> Any:
        """获取主键值"""
        return getattr(self, self.__mapper__.primary_key[0].name)

    @property
    def is_deleted(self) -> bool:
        """是否已删除"""
        return self.deleted_at is not None

    def __repr__(self) -> str:
        """模型的字符串表示"""
        return f"<{self.__class__.__name__}(id={self.primary_key_value})>"

    @classmethod
    async def get_by_id(cls: type[T], id: int) -> T | None:
        """通过ID获取记录"""
        stmt = sa.select(cls).where(cls.id == id)
        result = await cls.query_session.execute(stmt)
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
        result = await cls.query_session.execute(stmt)
        return list(result.scalars().all())

    @classmethod
    async def bulk_create(
        cls: type[T],
        items: list[dict[str, Any]],
        return_instances: bool = True
    ) -> list[T] | None:
        """批量创建记录"""
        try:
            instances = [cls(**item) for item in items]
            cls.query_session.add_all(instances)
            await cls.query_session.flush()
            await cls.query_session.commit()
            return instances if return_instances else None
        except Exception:
            await cls.query_session.rollback()
            raise

    @classmethod
    async def bulk_update(
        cls: type[T],
        items: list[tuple[int, dict[str, Any]]],
        return_instances: bool = True
    ) -> list[T] | None:
        """批量更新记录"""
        try:
            # 获取所有ID
            ids = [item[0] for item in items]
            # 构建更新映射
            update_map = {item[0]: item[1] for item in items}

            # 获取所有实例
            stmt = sa.select(cls).where(cls.id.in_(ids))
            result = await cls.query_session.execute(stmt)
            instances = list(result.scalars().all())

            # 更新实例
            for instance in instances:
                if instance.id in update_map:
                    for key, value in update_map[instance.id].items():
                        setattr(instance, key, value)

            await cls.query_session.flush()
            await cls.query_session.commit()
            return instances if return_instances else None
        except Exception:
            await cls.query_session.rollback()
            raise

    @classmethod
    async def bulk_delete(
        cls: type[T],
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

            await cls.query_session.execute(stmt)
            await cls.query_session.flush()
            await cls.query_session.commit()
        except Exception:
            await cls.query_session.rollback()
            raise
        finally:
            for id in ids:
                cls.release_lock(id)

    @classmethod
    async def bulk_restore(
        cls: type[T],
        ids: list[int],
        return_instances: bool = True
    ) -> list[T] | None:
        """批量恢复记录"""
        try:
            if not hasattr(cls, 'deleted_at'):
                raise AttributeError(f"{cls.__name__} 不支持软删除")

            stmt = (
                sa.update(cls)
                .where(cls.id.in_(ids))
                .values(deleted_at=None)
            )
            await cls.query_session.execute(stmt)
            await cls.query_session.flush()
            await cls.query_session.commit()

            if return_instances:
                stmt = sa.select(cls).where(cls.id.in_(ids))
                result = await cls.query_session.execute(stmt)
                return list(result.scalars().all())
            return None
        except Exception:
            await cls.query_session.rollback()
            raise

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
        result = await cls.query_session.execute(query)
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

        items = await cls.query_session.scalars(query)
        items = items.all()
        total = await cls.query_session.scalar(count_query) or 0

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
        return await cls.query_session.scalar(stmt) or 0

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

    async def to_api_dict(self) -> dict[str, Any]:
        """
        转换为API响应格式的字典
        默认排除一些敏感或内部字段
        """
        exclude_fields = ['password', 'deleted_at']
        return await self.to_dict(exclude=exclude_fields)

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


class AuditLogMixin(DatabaseModel):
    """
    审计日志混入类，提供数据变更记录和恢复功能
    """
    __abstract__ = True

    audit_log: Mapped[list[dict]] = mapped_column(
        sa.JSON,
        nullable=False,
        default=[],
        comment="审计日志记录"
    )

    def _record_change(
        self,
        action: str,
        changes: dict[str, Any],
        operator_id: int | None = None,
        comment: str | None = None
    ) -> None:
        """记录变更日志"""
        log_entry = {
            "action": action,
            "changes": changes,
            "operator_id": operator_id,
            "comment": comment,
            "timestamp": TimeZone.now().isoformat()
        }
        if not hasattr(self, 'audit_log'):
            self.audit_log = []
        self.audit_log.append(log_entry)

    async def update_with_audit(
        self,
        changes: dict[str, Any],
        operator_id: int | None = None,
        comment: str | None = None
    ) -> None:
        """带审计记录的更新操作"""
        old_values = {
            key: getattr(self, key)
            for key in changes.keys()
            if hasattr(self, key)
        }

        # 记录变更前的状态
        self._record_change(
            action="update",
            changes={
                "before": old_values,
                "after": changes
            },
            operator_id=operator_id,
            comment=comment
        )

        # 执行更新
        await super().update(**changes)

    async def delete_with_audit(
        self,
        operator_id: int | None = None,
        comment: str | None = None
    ) -> None:
        """带审计记录的删除操作"""
        self._record_change(
            action="delete",
            changes={
                "before": self._dict,
                "after": None
            },
            operator_id=operator_id,
            comment=comment
        )
        await super().delete()

    async def restore_to_version(
        self,
        version_index: int,
        operator_id: int | None = None,
        comment: str | None = None
    ) -> None:
        """恢复到指定版本"""
        if not 0 <= version_index < len(self.audit_log):
            raise ValueError("无效的版本索引")

        target_version = self.audit_log[version_index]
        if target_version["action"] == "update":
            old_state = target_version["changes"]["before"]

            # 记录恢复操作
            self._record_change(
                action="restore",
                changes={
                    "before": self._dict,
                    "after": old_state,
                    "restored_from_version": version_index
                },
                operator_id=operator_id,
                comment=comment
            )

            # 执行恢复
            await super().update(**old_state)

    def get_change_history(self) -> list[dict[str, Any]]:
        """获取变更历史"""
        return self.audit_log

    def get_version_at(self, version_index: int) -> dict[str, Any]:
        """获取指定版本的数据状态"""
        if not 0 <= version_index < len(self.audit_log):
            raise ValueError("无效的版本索引")

        version = self.audit_log[version_index]
        if version["action"] in ["update", "restore"]:
            return version["changes"]["before"]
        return {}