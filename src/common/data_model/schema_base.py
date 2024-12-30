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
    4. 生成列表 schema
"""
from typing import Any, Type, TypeVar

import sqlalchemy as sa

from pydantic import BaseModel, ConfigDict, Field, create_model

T = TypeVar('T', bound='SchemaBase')


class SchemaBase(BaseModel):
    """基础模型类"""
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)


def create_schema_model(
    model_cls: Type[Any],
    exclude: set[str] | None = None
) -> Type[SchemaBase]:
    """从 SQLAlchemy 模型创建 Pydantic 模型"""
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
        fields[column.name] = (python_type, None if column.nullable else ...)

    # 创建新的 SchemaBase 子类
    return create_model(
        f"{model_cls.__name__}Schema",
        __base__=SchemaBase,
        **fields
    )


def generate_schemas(
    model_cls: Type[Any],
    exclude_create: set[str] | None = None,
    exclude_update: set[str] | None = None,
    exclude_list: set[str] | None = None
) -> tuple[Type[SchemaBase], Type[SchemaBase], Type[SchemaBase], Type[BaseModel]]:
    """生成完整的 CRUD schemas"""
    # 基础 schema
    base_schema = create_schema_model(model_cls)

    # Create schema (排除 id 和时间戳)
    create_schema = create_schema_model(
        model_cls,
        exclude=exclude_create or {"id", "created_at", "updated_at", "deleted_at"}
    )

    # Update schema (排除 id 和时间戳)
    update_schema = create_schema_model(
        model_cls,
        exclude=exclude_update or {"id", "created_at", "updated_at", "deleted_at"}
    )

    # List schema
    class List(BaseModel):
        items: list[base_schema]  # type: ignore
        total: int = Field(default=0)
        page: int = Field(default=1)
        size: int = Field(default=20)

    return base_schema, create_schema, update_schema, List