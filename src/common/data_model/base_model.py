import asyncio

from datetime import datetime
from typing import Any, TypeVar

import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.utils.timezone import TimeZone

T = TypeVar('T', bound='DatabaseModel')


class DatabaseModel(AsyncAttrs, DeclarativeBase):
    """
    数据库模型基类，提供基础能力支持
    """
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
        async with self.lock:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            await self.query_session.flush()

    async def delete(self) -> None:
        """删除（带锁保护）"""
        async with self.lock:
            if hasattr(self, 'deleted_at'):
                self.deleted_at = TimeZone.now()
            else:
                await self.query_session.delete(self)
            await self.query_session.flush()
            self.release_lock(self.primary_key_value)

    async def restore(self) -> None:
        """恢复"""
        self.deleted_at = None
        await self.query_session.flush()

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


class BaseModelMixin(DatabaseModel):
    """
    模型扩展混入类，提供额外的功能
    """
    __abstract__ = True

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
        if _depth > max_depth:
            return {"id": self.id}

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