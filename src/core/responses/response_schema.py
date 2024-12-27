from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class ResponseSchema(BaseModel, Generic[T]):
    code: str
    message: str
    data: Optional[T] = None

    class Config:
        json_schema_extra = {
            "example": {
                "code": "200",
                "message": "成功",
                "data": None
            }
        } 