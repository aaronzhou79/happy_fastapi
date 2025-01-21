import inspect

from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Dict, Type, Union, get_args, get_origin

from pydantic import BaseModel
from sqlmodel import SQLModel


class TypeMapper:
    """类型映射工具"""

    python_to_ts_types = {
        str: "string",
        int: "number",
        float: "number",
        bool: "boolean",
        datetime: "Date",
        list: "Array<any>",
        dict: "Record<string, any>",
        None: "void"
    }

    @classmethod
    def to_typescript(cls, python_type: Type) -> str:
        """将Python类型转换为TypeScript类型"""
        # 处理Annotated类型
        origin = get_origin(python_type)
        if origin is Annotated:
            actual_type = get_args(python_type)[0]
            return cls.to_typescript(actual_type)

        if origin is not None:
            # 处理其他泛型类型
            args = get_args(python_type)
            if isinstance(origin, type):
                if issubclass(origin, list):
                    return f"Array<{cls.to_typescript(args[0])}>"
                if issubclass(origin, dict):
                    return f"Record<{cls.to_typescript(args[0])}, {cls.to_typescript(args[1])}>"

        # 处理基础类型
        if python_type in cls.python_to_ts_types:
            return cls.python_to_ts_types[python_type]

        # 处理枚举类型
        if inspect.isclass(python_type) and issubclass(python_type, Enum):
            return python_type.__name__

        # 处理Pydantic模型
        if inspect.isclass(python_type) and issubclass(python_type, (SQLModel, BaseModel)):
            return python_type.__name__

        return "any"

    @classmethod
    def model_to_interface(cls, model: Type[SQLModel | BaseModel]) -> str:
        """将Pydantic模型转换为TypeScript接口定义"""
        lines = [f"interface {model.__name__} {{"]

        for field_name, field in model.model_fields.items():
            if field.annotation:
                field_type = cls.to_typescript(field.annotation)
                lines.append(f"  {field_name}: {field_type};")
            else:
                lines.append(f"  {field_name}: any;")
        lines.append("}")
        return "\n".join(lines)

    @classmethod
    def enum_to_definition(cls, enum_class: Type[Enum]) -> str:
        """将Python Enum转换为TypeScript enum定义"""
        lines = [f"export enum {enum_class.__name__} {{"]

        for name, member in enum_class.__members__.items():
            if isinstance(member.value, str):
                lines.append(f"  {name} = '{member.value}',")
            else:
                lines.append(f"  {name} = {member.value},")

        lines.append("}")
        return "\n".join(lines)
