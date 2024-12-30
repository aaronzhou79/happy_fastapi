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
from typing import Any, Type, TypeVar

import sqlalchemy as sa

from pydantic import BaseModel, ConfigDict, Field, create_model
from sqlalchemy.sql.schema import ColumnDefault

T = TypeVar('T', bound='SchemaBase')


class SchemaBase(BaseModel):
    """基础模型类"""
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)


def create_schema_model(
    model_cls: Type[Any],
    schema_name: str | None = None,
    exclude: set[str] | None = None,
    include_relationships: bool = True,
    max_depth: int = 1
) -> Type[SchemaBase]:
    """从 SQLAlchemy 模型创建 Pydantic 模型

    Args:
        model_cls: SQLAlchemy 模型类
        schema_name: schema名称
        exclude: 排除的字段
        include_relationships: 是否包含关联字段
        max_depth: 关联数据的最大深度,默认为1
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
            python_type = python_type | None
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

            # 获取关联模型的schema
            related_schema = create_schema_model(
                rel.mapper.class_,
                exclude=exclude,
                include_relationships=True,
                max_depth=max_depth - 1
            )

            # 根据关系类型设置字段类型
            if rel.uselist:
                # 一对多/多对多关系
                field_type = list[related_schema]
                default_value = []
            else:
                # 一对一/多对一关系
                field_type = related_schema | None
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
) -> tuple[Type[SchemaBase], Type[SchemaBase], Type[SchemaBase]]:
    """生成完整的 CRUD schemas"""
    # 基础 schema
    base_schema = create_schema_model(
        model_cls,
        schema_name=f"{model_cls.__name__}Schema",
        max_depth=2
    )

    # Create schema (排除 id 和时间戳)
    create_schema = create_schema_model(
        model_cls,
        schema_name=f"{model_cls.__name__}Create",
        exclude=exclude_create or {"id", "created_at", "updated_at", "deleted_at"},
        include_relationships=False
    )

    # Update schema (排除 id 和时间戳)
    update_schema = create_schema_model(
        model_cls,
        schema_name=f"{model_cls.__name__}Update",
        exclude=exclude_update or {"id", "created_at", "updated_at", "deleted_at"},
        include_relationships=False
    )

    return base_schema, create_schema, update_schema