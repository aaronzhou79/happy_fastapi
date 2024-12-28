from enum import Enum
from typing import Any

from msgspec import json
from starlette.responses import JSONResponse


class ResponseCodeBase(Enum):
    """自定义状态码基类"""

    @property
    def code(self):
        """
        获取状态码
        """
        return self.value[0]

    @property
    def msg(self):
        """
        获取状态码信息
        """
        return self.value[1]


class ResponseCode(ResponseCodeBase):
    SUCCESS = (200, "请求成功")
    SUCCESS_CREATE = (201, '新建请求成功')
    SUCCESS_ACCEPTED = (202, '请求已接受，但处理尚未完成')
    SUCCESS_NO_CONTENT = (204, '请求成功，但没有返回内容')
    PARAMS_ERROR = (400, "请求参数错误")
    UNAUTHORIZED = (401, "未授权")
    FORBIDDEN = (403, "禁止访问")
    NOT_FOUND = (404, "资源不存在")
    RESOURCE_DELETED = (410, '请求的资源已永久删除')
    REQUEST_PARAMS_INVALID = (422, '请求参数非法')
    SERVER_ERROR = (500, "服务器内部错误")
    REQUEST_NOT_ALLOWED = (425, '无法执行请求，由于服务器无法满足要求')
    REQUEST_TOO_MANY = (429, '请求过多，服务器限制')
    GATEWAY_ERROR = (502, '网关错误')
    SERVICE_UNAVAILABLE = (503, '服务器暂时无法处理请求')
    GATEWAY_TIMEOUT = (504, '网关超时')
    UNKNOWN_ERROR = (999, "未知错误")


class ResponseMessage:
    zh_CN = {
        ResponseCode.SUCCESS: "请求成功",
        ResponseCode.SUCCESS_CREATE: "新建请求成功",
        ResponseCode.SUCCESS_ACCEPTED: "请求已接受，但处理尚未完成",
        ResponseCode.SUCCESS_NO_CONTENT: "请求成功，但没有返回内容",
        ResponseCode.PARAMS_ERROR: "请求参数错误",
        ResponseCode.UNAUTHORIZED: "未授权",
        ResponseCode.FORBIDDEN: "禁止访问",
        ResponseCode.NOT_FOUND: "资源不存在",
        ResponseCode.RESOURCE_DELETED: "请求的资源已永久删除",
        ResponseCode.REQUEST_PARAMS_INVALID: "请求参数非法",
        ResponseCode.SERVER_ERROR: "服务器内部错误",
        ResponseCode.REQUEST_NOT_ALLOWED: "无法执行请求，由于服务器无法满足要求",
        ResponseCode.REQUEST_TOO_MANY: "请求过多，服务器限制",
        ResponseCode.GATEWAY_ERROR: "网关错误",
        ResponseCode.SERVICE_UNAVAILABLE: "服务器暂时无法处理请求",
        ResponseCode.GATEWAY_TIMEOUT: "网关超时",
    }


class MsgSpecJSONResponse(JSONResponse):
    """
    JSON response using the high-performance msgspec library to serialize data to JSON.
    """
    def render(self, content: Any) -> bytes:
        def convert_enum(obj):
            if isinstance(obj, ResponseCode):
                return {"code": obj.code, "msg": obj.msg}
            return obj

        return json.encode(content, enc_hook=convert_enum)