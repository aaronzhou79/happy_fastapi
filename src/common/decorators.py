from typing import Callable, Type, TypeVar

from sqlmodel import SQLModel

T = TypeVar("T", bound=SQLModel)


def optional_fields(exclude_fields: set[str] | None = None) -> Callable[[Type[T]], Type[T]]:
    """将模型的所有字段设置为可选(除了exclude_fields中的字段)"""
    if exclude_fields is None:
        exclude_fields = {'id'}

    def decorator(cls: Type[T]) -> Type[T]:
        # 获取所有字段
        for field_name, field in cls.model_fields.items():
            if field_name not in exclude_fields:
                # 创建新的字段定义
                field.default = None
                if field.annotation:
                    field.annotation = field.annotation | None  # type: ignore
                setattr(field, 'required', False)
                # 更新__annotations__
                cls.__annotations__[field_name] = field.annotation

        # 重建模型
        cls.model_rebuild()
        return cls
    return decorator