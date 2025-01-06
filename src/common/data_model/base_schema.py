from typing import Any, Optional, Type, TypeVar

from pydantic import BaseModel, ConfigDict, create_model
from sqlalchemy import inspect
from sqlalchemy.orm import RelationshipProperty

from src.common.data_model.base_model import Base, DatabaseModel
from src.common.enums import StrEnum

# 泛型类型变量
ModelType = TypeVar("ModelType", bound=DatabaseModel)


class BaseSchema(BaseModel):
    """
    基础 Schema 类
    """
    model_config = ConfigDict(
        use_enum_values=True,
        from_attributes=True,
        populate_by_name=True
    )


CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)
BaseSchemaType = TypeVar("BaseSchemaType", bound=BaseSchema)
WithSchemaType = TypeVar("WithSchemaType", bound=BaseSchema)

class UpdateSchema(BaseSchema):
    """
    更新 Schema 类
    """
    model_config = ConfigDict(
        use_enum_values=True,
        from_attributes=True,
        populate_by_name=True
    )


class SchemaType(StrEnum):
    """
    Schema 类型
    """
    BASE = "base"
    CREATE = "create"
    UPDATE = "update"


def _process_column(
    column: Any,
    generate_type: SchemaType
) -> tuple[type | None, Any]:
    """处理数据库列的类型和默认值"""
    column_type = column.type.python_type

    match generate_type:
        case SchemaType.BASE:
            column_nullable = column.nullable
            default_value = ... if column.default is None else column.default.arg
        case SchemaType.CREATE:
            if column.name in ["deleted_at", "created_at", "updated_at", "id"]:
                return None, None
            column_nullable = column.nullable
            default_value = ... if column.default is None else column.default.arg
        case SchemaType.UPDATE:
            if column.name in ["deleted_at", "created_at", "updated_at"]:
                return None, None
            column_nullable = True
            default_value = None

    field_type = Optional[column_type] if column_nullable else column_type  # noqa: UP007
    return field_type, default_value


def _process_relationship(
    relationship: RelationshipProperty,
    generate_type: SchemaType,
) -> tuple[type | None, Any]:
    """处理关系字段的类型"""
    related_model = relationship.mapper.class_
    if relationship.uselist:
        field_type = list[generate_schema(related_model, generate_type, prefix=f"{related_model.__name__}")]
    else:
        field_type = generate_schema(related_model, generate_type, prefix=f"{related_model.__name__}")

    if relationship.direction.name in ("MANYTOONE", "ONETOONE"):
        field_type = Optional[field_type]  # noqa: UP007

    return field_type, None


def generate_schema(
    model: Type[Base],
    generate_type: SchemaType = SchemaType.BASE,
    *,
    prefix: str = "",
    include_relationships: list[str] | None = None,
    exclude_fields: list[str] | None = None
) -> Type[BaseSchema]:
    """根据 SQLAlchemy 模型生成对应的 Pydantic 模型"""
    if include_relationships is None:
        include_relationships = []

    mapper = inspect(model)
    fields: dict[str, Any] = {}

    # 处理列
    for column in mapper.columns:
        if exclude_fields and column.name in exclude_fields:
            continue
        field_type, default_value = _process_column(column, generate_type)
        if field_type is not None:
            fields[column.name] = (field_type, default_value)

    # 处理关系
    if include_relationships:
        for name, relationship in mapper.relationships.items():
            if name in include_relationships:
                field_type, default_value = _process_relationship(relationship, generate_type)
                fields[name] = (field_type, default_value)

    return create_model(
        f"{prefix.capitalize()}{model.__name__}Schema{str(generate_type.value).capitalize()}",
        __base__=BaseSchema,
        **fields
    )

