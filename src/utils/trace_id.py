# src/utils/trace_id.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : trace_id.py
# @Software: Cursor
# @Description: 获取请求 trace_id

from fastapi import Request

from src.core.conf import settings


def get_request_trace_id(request: Request) -> str:
    """
    获取请求 trace_id
    """
    return request.headers.get(settings.TRACE_ID_REQUEST_HEADER_KEY) or '-'
