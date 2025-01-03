# src/core/responses/response_schema.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/01/02
# @Author  : Aaron Zhou
# @File    : response_schema.py
# @Software: Cursor
# @Description: 响应数据模型

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel

from src.core.conf import settings

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """
    响应数据模型
    """
    code: int
    msg: str
    data: T | str | None = None

    class Config:
        json_encoders = {datetime: lambda x: x.strftime(settings.DATETIME_FORMAT)}
        json_schema_extra = {
            "example": {
                "code": "200",
                "msg": "成功",
                "data": None
            }
        }
