# src/common/data_model/base_model.py

import asyncio

from datetime import datetime
from typing import Annotated, Any, TypeVar

import sqlalchemy as sa

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import RelationshipProperty
from sqlmodel import Field, SQLModel

from src.core.conf import settings
from src.database.db_session import AuditAsyncSession, async_session
from src.utils.snowflake import id_worker
from src.utils.timezone import TimeZone

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
        """查询会话"""
        return async_session()

    def __tablename__(self) -> str:
        """表名"""
        return self.__name__.lower()

    async def to_dict(
        self,
        *,
        exclude: list[str] | None = None,
        include: list[str] | None = None,
        max_depth: int = 2,
        limit: int = 20,
        _depth: int = 1,
        _visited: set | None = None
    ) -> dict[str, Any]:
        """转换为字典,支持递归加载关联对象

        Args:
            exclude: 排除的字段列表
            include: 包含的字段列表
            max_depth: 最大递归深度
            _depth: 当前递归深度
            _visited: 已访问对象集合,用于检测循环引用

        Returns:
            dict: 转换后的字典
        """
        # 初始化已访问集合
        if _visited is None:
            _visited = set()

        # 检查是否已访问过该对象,避免循环引用
        obj_id = id(self)
        if obj_id in _visited:
            return {
                "id": getattr(self, "id", None),
                "name": getattr(self, "name", None),
                "code": getattr(self, "code", None)}

        _visited.add(obj_id)

        # 如果超过最大深度, 只返回基础对象
        if _depth > max_depth:
            return {
                "id": getattr(self, "id", None),
                "name": getattr(self, "name", None),
                "code": getattr(self, "code", None)}

        # 获取基础字段数据
        data = self.model_dump(exclude_none=True)

        # 应用include/exclude过滤
        if include:
            data = {k: v for k, v in data.items() if k in include}
        if exclude:
            data = {k: v for k, v in data.items() if k not in exclude}

        # 获取所有relationship
        mapper = inspect(self.__class__)
        relationships = [
            attr for attr in mapper.attrs
            if isinstance(attr, RelationshipProperty)
        ]

        # 处理每个relationship
        for rel in relationships:
            key = rel.key
            if exclude and key in exclude:
                continue
            if include and key not in include:
                continue

            # 获取关联对象
            try:
                value = await getattr(self.awaitable_attrs, key)
            except Exception as e:
                print(f"获取关联对象失败: {self.__class__.__name__}.{key} - {str(e)}")
                continue

            # 处理关联对象
            if value is None:
                data[key] = None
            elif isinstance(value, list):
                # 处理集合关联,只取前20条
                limited_value = value[:limit]
                data[key] = [
                    await item.to_dict(
                        exclude=exclude,
                        include=include,
                        max_depth=max_depth,
                        _depth=_depth + 1,
                        _visited=_visited
                    ) if hasattr(item, "to_dict") else item
                    for item in limited_value
                ]
                # 等待所有异步操作完成
                if data[key] and isinstance(data[key][0], list):
                    data[key] = await asyncio.gather(*data[key])
            else:
                # 处理单个关联对象
                data[key] = await value.to_dict(
                    exclude=exclude,
                    include=include,
                    max_depth=max_depth,
                    _depth=_depth + 1,
                    _visited=_visited
                ) if hasattr(value, "to_dict") else value

        return data

    async def to_api_dict(self, max_depth: int = 2) -> dict[str, Any]:
        """转换为API响应格式的字典"""
        exclude_fields = ['password']
        return await self.to_dict(exclude=exclude_fields, max_depth=max_depth)

    def __repr__(self) -> str:
        """字符串表示"""
        return f"<{self.__class__.__name__} id={getattr(self, 'id', None)}, name={getattr(self, 'name', None)}, code={getattr(self, 'code', None)}>"


async def create_table() -> None:
    """创建表"""
    from src.database.db_session import async_engine
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
