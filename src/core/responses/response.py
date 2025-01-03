# src/core/responses/response.py
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024/12/29
# @Author  : Aaron Zhou
# @File    : response.py
# @Software: Cursor
# @Description: 统一数据返回模型
from typing import Any

from fastapi import Response

from src.core.responses.response_code import MsgSpecJSONResponse, ResponseCode, ResponseCodeBase

from .response_schema import ResponseModel

__all__ = ['ResponseModel', 'response_base']


class ResponseBase:
    """
    统一返回方法

    .. tip::

        此类中的方法将返回 ResponseSchema 模型，作为一种编码风格而存在；

    E.g. ::

        @router.get('/test')
        def test() -> ResponseSchema:
            return response.success(data={'test': 'test'})
    """

    @staticmethod
    def __response(*, res: ResponseCodeBase = ResponseCode.SUCCESS, data: Any | None = None) -> ResponseModel:
        """
        请求成功返回通用方法

        :param res: 返回信息
        :param data: 返回数据
        :return:
        """
        return ResponseModel(code=res.code, msg=res.msg, data=data)

    def success(
        self,
        *,
        res: ResponseCodeBase = ResponseCode.SUCCESS,
        data: Any | None = None,
    ) -> ResponseModel:
        return self.__response(res=res, data=data)

    def fail(
        self,
        *,
        res: ResponseCodeBase = ResponseCode.PARAMS_ERROR,
        data: Any = None,
    ) -> ResponseModel:
        return self.__response(res=res, data=data)

    @staticmethod
    def fast_success(
        *,
        res: ResponseCode = ResponseCode.SUCCESS,
        data: Any | None = None,
    ) -> Response:
        """
        此方法是为了提高接口响应速度而创建的，如果返回数据无需进行 pydantic 解析和验证，则推荐使用，相反，请不要使用！

        .. warning::

            使用此返回方法时，不要指定接口参数 response_model，也不要在接口函数后添加箭头返回类型

        :param res:
        :param data:
        :return:
        """
        return MsgSpecJSONResponse({'code': res.code, 'msg': res.msg, 'data': data})


response_base = ResponseBase()
