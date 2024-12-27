from enum import Enum
from typing import Any
from msgspec import json
from starlette.responses import JSONResponse

class ResponseCode(str, Enum):
    SUCCESS = "200"
    PARAMS_ERROR = "400"
    UNAUTHORIZED = "401"
    FORBIDDEN = "403"
    NOT_FOUND = "404"
    SERVER_ERROR = "500"

class ResponseMessage:
    zh_CN = {
        ResponseCode.SUCCESS: "成功",
        ResponseCode.PARAMS_ERROR: "参数错误",
        ResponseCode.UNAUTHORIZED: "未授权",
        ResponseCode.FORBIDDEN: "禁止访问",
        ResponseCode.NOT_FOUND: "资源不存在",
        ResponseCode.SERVER_ERROR: "服务器内部错误"
    }


class MsgSpecJSONResponse(JSONResponse):
    """
    JSON response using the high-performance msgspec library to serialize data to JSON.
    """
    def render(self, content: Any) -> bytes:
        return json.encode(content)