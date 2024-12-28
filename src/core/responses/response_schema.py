from datetime import datetime
from typing import Any

from pydantic import BaseModel

from src.core.conf import settings


class ResponseSchema(BaseModel):
    """
    响应数据模型
    """
    code: int
    msg: str
    data: Any | None = None

    class Config:
        json_encoders = {datetime: lambda x: x.strftime(settings.DATETIME_FORMAT)}
        json_schema_extra = {
            "example": {
                "code": "200",
                "msg": "成功",
                "data": None
            }
        }
