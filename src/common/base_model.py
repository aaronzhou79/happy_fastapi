# src/common/data_model/base_model.py

import asyncio

from datetime import datetime
from typing import Annotated, Any, Dict, TypeVar

import sqlalchemy as sa

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import RelationshipProperty
from sqlmodel import Field, SQLModel

from src.core.conf import settings
from src.database.db_session import AuditAsyncSession
from src.middleware.state_middleware import UserState
from src.utils.snowflake import id_worker
from src.utils.timezone import TimeZone

ModelType = TypeVar("ModelType", bound='DatabaseModel')
CreateModelType = TypeVar("CreateModelType", bound=SQLModel)
UpdateModelType = TypeVar("UpdateModelType", bound=SQLModel)

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
    created_by: int | None = Field(
        default_factory=UserState.get_current_user_id,
        sa_column_kwargs={"comment": "创建者"}
    )
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": TimeZone.now, "comment": "更新时间"}
    )
    updated_by: int | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": UserState.get_current_user_id, "comment": "更新者"}
    )


class DatabaseModel(AsyncAttrs, SQLModel):
    """数据库模型基类"""
    __abstract__ = True
    id: id_pk  # type: ignore
    class Config:
        from_attributes = True
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True

    async def to_dict(  # noqa: C901
        self,
        *,
        exclude: list[str] | None = None,
        include: list[str] | None = None,
        max_depth: int = 1,
        limit: int = 20,
        _depth: int = 1,
        _visited: set | None = None
    ) -> dict[str, Any]:
        """转换为字典,支持递归加载关联对象

        Args:
            exclude: 排除的字段列表
            include: 包含的字段列表
            max_depth: 最大递归深度
            limit: 关联的对象数量返回的数量
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

    async def to_api_dict(
        self,
        max_depth: int = 1
    ) -> dict[str, Any]:
        """转换为API响应格式的字典"""
        exclude_fields = ['password']
        return await self.to_dict(exclude=exclude_fields, max_depth=max_depth)

    def __repr__(self) -> str:
        """字符串表示"""
        return f"<{self.__class__.__name__} id={getattr(self, 'id', None)}, name={getattr(self, 'name', None)}, code={getattr(self, 'code', None)}>"  # noqa: E501

    @declared_attr.directive
    def __tablename__(self) -> str:
        """表名"""
        return self.__name__.lower()

    @declared_attr.directive
    def __foreign_info__(self) -> dict[str, dict]:
        """获取外键信息"""
        try:
            mapper = inspect(self)
            if not mapper:
                return {}

            foreign_keys_info = {}
            for table in mapper.persist_selectable.foreign_keys:
                foreign_keys_info[table.parent.name] = {
                    'target_table': table.column.table.name,
                    'target_column': table.column.name
                }
        except Exception:
            return {}

        return foreign_keys_info

    @declared_attr.directive
    def __relation_info__(self) -> dict[str, dict]:
        """获取关系信息"""
        mapper = inspect(self)
        if not mapper:
            return {}

        relation_info = {}
        for rel_name, rel in mapper.relationships.items():
            if rel.secondary is not None:
                break

            relation_info[rel_name] = {
                'relation_type': rel.direction.name,
                'relation_model': rel.mapper.class_,
                'relation_table': rel.mapper.class_.__tablename__,
                'relation_column': rel.key,
                'remote_column': rel.remote_side,
            }
        return relation_info

    @declared_attr.directive
    def __field_info__(self) -> dict[str, dict]:
        """获取基础字段信息"""
        try:
            mapper = inspect(self)
            if not mapper:
                return {}

            field_info = {}
            for column in mapper.persist_selectable.columns:
                field_info[column.name] = {
                    'type': str(column.type),
                    'nullable': column.nullable,
                    'primary_key': column.primary_key,
                    'default': str(column.default.arg) if column.default else None,
                    'comment': column.comment,
                    'unique': column.unique,
                    'index': column.index,
                }
        except Exception:
            return {}
        return field_info

    @declared_attr.directive
    def __nested_field_info__(self) -> dict[str, dict]:
        """获取嵌套字段信息"""
        return {
            "foreign_info": self.__foreign_info__,
            "relation_info": self.__relation_info__,
            "field_info": self.__field_info__
        }

    @classmethod
    async def create(
        cls,
        db: AuditAsyncSession,
        obj_in: CreateModelType | ModelType | Dict[str, Any]
    ) -> Any:
        """创建对象"""
        exclude_fields = {
            "id", "created_at", "updated_at", "deleted_at",
            "created_by", "updated_by", "_sa_instance_state"
        } | set(cls.__relation_info__.keys())

        if isinstance(obj_in, dict):
            create_data = {k: v for k, v in obj_in.items() if k not in exclude_fields}
        else:
            create_data = obj_in.model_dump(
                exclude_unset=True,
                exclude=exclude_fields,
            )

        db_obj = cls(**create_data)
        db.add(db_obj)
        await db.flush()
        return db_obj


async def create_table() -> None:
    """创建表"""
    from src.database.db_session import async_engine
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
