from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseSchema(BaseModel, Generic[T]):
    code: str
    message: str
    data: T | None = None

    class Config:
        arbitrary_types_allowed = True  # 允许任意类型
        from_attributes = True  # 支持从对象属性读取
        json_schema_extra = {
            "example": {
                "code": "200",
                "message": "成功",
                "data": None
            }
        }
