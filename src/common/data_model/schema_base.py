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
from typing import Any, Type, TypeVar, Optional, Set

import sqlalchemy as sa

from pydantic import BaseModel, ConfigDict, Field, create_model
from sqlalchemy.sql.schema import ColumnDefault
from sqlalchemy.orm.relationships import RelationshipProperty

T = TypeVar('T', bound='SchemaBase')


class SchemaBase(BaseModel):
    """基础模型类"""
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)


def create_schema_model(
    model_cls: Type[Any],
    schema_name: str | None = None,
    exclude: set[str] | None = None,
    include_relationships: bool = True,
    include_many: bool = False,  # 是否包含一对多关系
    max_depth: int = 1,
    _parent_type: Type[Any] | None = None  # 防止循环引用
) -> Type[SchemaBase]:
    """从 SQLAlchemy 模型创建 Pydantic 模型

    Args:
        model_cls: SQLAlchemy 模型类
        schema_name: schema名称
        exclude: 排除的字段
        include_relationships: 是否包含关联字段
        include_many: 是否包含一对多关系字段
        max_depth: 关联数据的最大深度,默认为1
        _parent_type: 父级模型类型,用于防止循环引用
    """
    # 获取模型信息
    mapper = sa.inspect(model_cls)
    fields = {}
    exclude = exclude or set()

    # 处理普通字段
    for column in mapper.columns:
        if column.name in exclude:
            continue
        python_type = column.type.python_type
        if column.nullable:
            python_type = Optional[python_type]
        # 获取默认值
        default = None
        if column.default is not None:
            if isinstance(column.default, ColumnDefault):
                default = column.default.arg
            else:
                default = column.default
        # 创建带有描述和默认值的字段
        field = Field(
            default if default is not None else (None if column.nullable else ...),
            description=column.comment,
        )
        fields[column.name] = (python_type, field)

    # 处理关联字段
    if include_relationships and max_depth > 0:
        for name, rel in mapper.relationships.items():
            if name in exclude:
                continue

            # 跳过父级类型,防止循环引用
            if _parent_type and rel.mapper.class_ == _parent_type:
                continue

            # 获取关联模型的schema
            related_schema = create_schema_model(
                rel.mapper.class_,
                exclude=exclude,
                include_relationships=True,
                include_many=include_many,
                max_depth=max_depth - 1,
                _parent_type=model_cls
            )

            # 根据关系类型设置字段类型
            if rel.uselist:  # 一对多关系
                if include_many:
                    field_type = list[related_schema]
                    default_value = []
                else:
                    continue  # 不包含一对多关系时跳过
            else:  # 一对一/多对一关系
                field_type = Optional[related_schema]
                default_value = None

            fields[name] = (field_type, Field(default=default_value))

    # 创建新的 SchemaBase 子类
    return create_model(
        schema_name or f"{model_cls.__name__}Schema",
        __base__=SchemaBase,
        **fields
    )


def generate_schemas(
    model_cls: Type[Any],
    exclude_create: set[str] | None = None,
    exclude_update: set[str] | None = None,
    include_relationships: set[str] | None = None,  # 需要包含的关系字段
) -> tuple[Type[SchemaBase], Type[SchemaBase], Type[SchemaBase]]:
    """生成完整的 CRUD schemas

    Args:
        model_cls: SQLAlchemy 模型类
        exclude_create: 创建时排除的字段
        exclude_update: 更新时排除的字段
        include_relationships: 需要包含的关系字段名称集合
    """
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