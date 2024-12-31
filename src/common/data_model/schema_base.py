# src/common/data_model/schema_base.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : schema_base.py
# @Software: Cursor
# @Description: schema_base 数据模型类
"""
    用于生成 CRUD 的 schema

    1. 生成基础 schema
    2. 生成创建 schema
    3. 生成更新 schema
"""
from typing import Any, Type, TypeVar, Optional, Set, Tuple, Dict, Union

import sqlalchemy as sa
from sqlalchemy.dialects.mysql import JSON, LONGTEXT
from sqlalchemy.types import TypeEngine

from pydantic import BaseModel, ConfigDict, Field, create_model
from sqlalchemy.sql.schema import ColumnDefault
from sqlalchemy.orm.relationships import RelationshipProperty

T = TypeVar('T', bound='SchemaBase')


class SchemaBase(BaseModel):
    """基础模型类"""
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)


def get_python_type(column: sa.Column) -> Type:
    """获取列的 Python 类型"""
    try:
        # 尝试获取 python_type
        return column.type.python_type
    except NotImplementedError:
        # 处理特殊类型
        if isinstance(column.type, (JSON, sa.JSON)):
            return Dict[str, Any]
        elif isinstance(column.type, LONGTEXT):
            return str
        elif isinstance(column.type, sa.Enum):
            return str
        elif isinstance(column.type, sa.ARRAY):
            return list
        else:
            # 默认返回 Any
            return Any


def create_schema_model(
    model_cls: Type[Any],
    schema_name: str | None = None,
    exclude: set[str] | None = None,
    include_relationships: bool = True,
    include_many: bool = False,
    max_depth: int = 1,
    _parent_type: Type[Any] | None = None
) -> Type[SchemaBase]:
    """从 SQLAlchemy 模型创建 Pydantic 模型"""
    mapper = sa.inspect(model_cls)
    fields = {}
    exclude = exclude or set()

    # 处理普通字段
    for column in mapper.columns:
        if column.name in exclude:
            continue

        # 获取 Python 类型
        python_type = get_python_type(column)

        if column.nullable:
            python_type = Optional[python_type]

        # 获取默认值
        default = None
        if column.default is not None:
            if isinstance(column.default, ColumnDefault):
                default = column.default.arg
            else:
                default = column.default

        # 创建字段
        field = Field(
            default if default is not None else (None if column.nullable else ...),
            description=column.comment,
        )
        fields[column.name] = (python_type, field)

    # 处理关系字段
    if include_relationships and max_depth > 0:
        for name, rel in mapper.relationships.items():
            if name in exclude:
                continue

            if _parent_type and rel.mapper.class_ == _parent_type:
                continue

            related_schema = create_schema_model(
                rel.mapper.class_,
                exclude=exclude,
                include_relationships=True,
                include_many=include_many,
                max_depth=max_depth - 1,
                _parent_type=model_cls
            )

            if rel.uselist:
                if include_many:
                    field_type = list[related_schema]
                    default_value = []
                else:
                    continue
            else:
                field_type = Optional[related_schema]
                default_value = None

            fields[name] = (field_type, Field(default=default_value))

    return create_model(
        schema_name or f"{model_cls.__name__}Schema",
        __base__=SchemaBase,
        **fields
    )


def generate_schemas(
    model_cls: Type[Any],
    exclude_create: set[str] | None = None,
    exclude_update: set[str] | None = None,
    include_relationships: set[str] | None = None,
) -> Tuple[Type[T], Type[T], Type[T]]:
    """生成完整的 CRUD schemas"""
    # 基础 schema (包含所有字段)
    base_schema = create_schema_model(
        model_cls,
        schema_name=f"{model_cls.__name__}Schema",
        max_depth=2
    )

    # 默认排除的字段
    default_exclude = {"id", "created_at", "updated_at", "deleted_at"}

    # Create schema
    create_exclude = (exclude_create or default_exclude) - (include_relationships or set())
    create_schema = create_schema_model(
        model_cls,
        schema_name=f"{model_cls.__name__}Create",
        exclude=create_exclude,
        include_relationships=True,
        include_many=True,
        max_depth=1
    )

    # Update schema
    update_exclude = (exclude_update or default_exclude) - (include_relationships or set())
    update_schema = create_schema_model(
        model_cls,
        schema_name=f"{model_cls.__name__}Update",
        exclude=update_exclude,
        include_relationships=True,
        include_many=True,
        max_depth=1
    )

    return base_schema, create_schema, update_schema