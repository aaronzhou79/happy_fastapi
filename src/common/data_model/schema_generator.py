from __future__ import annotations

from typing import Any, Generic, TypeVar
from pydantic import BaseModel, ConfigDict, create_model
from sqlalchemy import Column, inspect as sa_inspect

from src.common.data_model.base_model import BaseModelMixin

ModelT = TypeVar("ModelT", bound=BaseModelMixin)

class PydanticSchemaGenerator(Generic[ModelT]):
    def __init__(self, model: type[ModelT]) -> None:
        self.model = model
        self.inspector = sa_inspect(model)

    def _get_model_fields(
        self,
        model: Any,
        exclude: set[str] | None = None,
        include: set[str] | None = None,
        make_optional: bool = False
    ) -> dict[str, tuple[type, Any]]:
        """
        获取模型的所有字段
        :param model: SQLAlchemy 模型
        :param exclude: 要排除的字段集合
        :param include: 要包含的字段集合
        :param make_optional: 是否将字段设置为可选
        :return: 字段定义字典
        """
        exclude = exclude or set()
        include = include or set()
        fields: dict[str, tuple[type, Any]] = {}

        inspector = sa_inspect(model)
        for column in inspector.columns:
            if column.key in exclude or (include and column.key not in include):
                continue

            python_type = self._get_column_type(column)
            default_value = None if make_optional else ...
            fields[column.key] = (python_type, default_value)

        return fields

    def generate_with_relationships(
        self,
        *,
        name_prefix: str = "",
        exclude: set[str] | None = None,
        include: set[str] | None = None,
        relation_exclude: dict[str, set[str]] | None = None,
    ) -> type[BaseModel]:
        """
        生成包含关系的模型，自动包含关联表的所有基础字段
        :param name_prefix: 类名前缀
        :param exclude: 要排除的主模型字段
        :param include: 要包含的主模型字段
        :param relation_exclude: 每个关系要排除的字段，格式为 {"关系名": {"field1", "field2"}}
        """
        exclude = exclude or set()
        include = include or set()
        relation_exclude = relation_exclude or {}

        # 获取主模型字段
        fields = self._get_model_fields(
            self.model,
            exclude=exclude,
            include=include
        )

        # 处理关系字段
        for rel_name, rel in self.inspector.relationships.items():
            if rel_name in exclude or (include and rel_name not in include):
                continue

            related_model = rel.mapper.class_
            # 获取关系模型的所有字段
            related_fields = self._get_model_fields(
                related_model,
                exclude=relation_exclude.get(rel_name, set())
            )

            # 创建关系引用模式
            ref_schema = create_model(
                f"{related_model.__name__}Ref",
                __config__=ConfigDict(
                    from_attributes=True,
                    populate_by_name=True
                ),
                **related_fields,   # type: ignore
            )   # type: ignore

            # 设置字段类型
            field_type = list[ref_schema] if rel.uselist else ref_schema  # type: ignore
            fields[rel_name] = (field_type, None)

        # 创建新的模型类
        return create_model(
            f"{name_prefix}{self.model.__name__}WithRelations",
            __config__=ConfigDict(
                from_attributes=True,
                populate_by_name=True
            ),
            **fields,   # type: ignore
        )   # type: ignore



    def generate_base(
        self,
        *,
        name_prefix: str = "",
        exclude: set[str] | None = None,
        include: set[str] | None = None,
    ) -> type[BaseModel]:
        """生成基础模式"""
        exclude = exclude or set()
        include = include or set()

        fields = {
            column.key: (self._get_python_type(column), ...)
            for column in self.inspector.columns
            if column.key not in exclude and (not include or column.key in include)
        }

        return create_model(
            f"{name_prefix}{self.model.__name__}",
            __config__=ConfigDict(from_attributes=True),
            **fields,   # type: ignore
        )   # type: ignore

    def _get_python_type(self, column: Column) -> type:
        """获取列的 Python 类型"""
        python_type = column.type.python_type
        if column.nullable:
            return python_type | None  # type: ignore
        return python_type

    def generate_create(
        self,
        *,
        name_prefix: str = "",
        exclude: set[str] | None = None,
    ) -> type[BaseModel]:
        """生成创建模式"""
        return self.generate_base(
            name_prefix=f"{name_prefix}Create",
            exclude=exclude,
        )

    def generate_update(
        self,
        *,
        name_prefix: str = "",
        exclude: set[str] | None = None,
    ) -> type[BaseModel]:
        """生成更新模式，所有字段都是可选的"""
        exclude = exclude or set()

        fields = self._get_model_fields(
            self.model,
            exclude=exclude,
            make_optional=True
        )

        return create_model(
            f"{name_prefix}Update{self.model.__name__}",
            __config__=ConfigDict(
                from_attributes=True,
                populate_by_name=True
            ),
            **fields,   # type: ignore
        )   # type: ignore

    def generate_list(
        self,
        *,
        name_prefix: str = "",
        exclude: set[str] | None = None,
        include: set[str] | None = None,
        page_size: int = 20,
    ) -> type[BaseModel]:
        """
        生成列表响应模型
        :param name_prefix: 类名前缀
        :param exclude: 要排除的字段
        :param include: 要包含的字段
        :param page_size: 默认分页大小
        """
        exclude = exclude or set()
        include = include or set()

        # 获取基础字段
        fields = self._get_model_fields(
            self.model,
            exclude=exclude,
            include=include
        )

        # 创建列表项模型
        list_item_model = create_model(
            f"{name_prefix}{self.model.__name__}ListItem",
            __config__=ConfigDict(
                from_attributes=True,
                populate_by_name=True,
                json_schema_extra={
                    "example": {
                        "items": [],
                        "total": 0,
                        "page": 1,
                        "size": page_size
                    }
                }
            ),
            **fields   # type: ignore
        )   # type: ignore

        # 创建列表响应模型
        return create_model(
            f"{name_prefix}{self.model.__name__}List",
            __config__=ConfigDict(
                from_attributes=True,
                populate_by_name=True
            ),
            items=(list[list_item_model], []),
            total=(int, 0),
            page=(int, 1),
            size=(int, page_size)
        )

    def _get_column_type(self, column: Column) -> type:
        """获取列的类型"""
        if isinstance(column, Column):
            python_type = column.type.python_type
            return python_type | None if column.nullable else python_type  # type: ignore
        return str  # 默认返回字符串类型

def generate_schemas(
    model: type[ModelT],
    *,
    prefix: str = "",
    exclude_base: set[str] | None = None,
    exclude_create: set[str] | None = None,
    exclude_update: set[str] | None = None,
    exclude_relations: set[str] | None = None,
) -> dict[str, type[BaseModel]]:
    """
    为模型生成所有常用的 Pydantic 模式
    :param model: SQLAlchemy 模型
    :param prefix: 类名前缀
    :param exclude_base: 基础模式要排除的字段
    :param exclude_create: 创建模式要排除的字段
    :param exclude_update: 更新模式要排除的字段
    :param exclude_relations: 关系模式要排除的字段
    :return: 模式字典
    """
    generator = PydanticSchemaGenerator(model)

    # 设置默认排除字段
    exclude_base = exclude_base or set()
    exclude_create = exclude_create or {"id", "created_at", "updated_at", "deleted_at"}
    exclude_update = exclude_update or {"id", "created_at", "updated_at", "deleted_at"}
    exclude_relations = exclude_relations or set()

    # 生成模式
    base_schema = generator.generate_base(
        name_prefix=prefix,
        exclude=exclude_base
    )

    return {
        "Base": base_schema,
        "Create": generator.generate_create(
            name_prefix=prefix,
            exclude=exclude_create
        ),
        "Update": generator.generate_update(
            name_prefix=prefix,
            exclude=exclude_update
        ),
        "WithRelations": generator.generate_with_relationships(
            name_prefix=prefix,
            exclude=exclude_relations
        ),
        "List": generator.generate_list(
            name_prefix=prefix,
            exclude=exclude_base
        )
    }