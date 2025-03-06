# src/middleware/state_middleware.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : state_middleware.py
# @Software: Cursor
# @Description: 请求 state 中间件
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.core.user_state import _request_ctx_var
from src.utils.request_parse import parse_ip_info, parse_user_agent_info

__all__ = ["StateMiddleware"]


class StateMiddleware(BaseHTTPMiddleware):
    """请求 state 中间件"""

    @classmethod
    def get_current_request(cls) -> int:
        """获取当前请求"""
        request = _request_ctx_var.get()
        if request and hasattr(request, "user_id"):
            return getattr(request, "user_id", 0)

        return 0

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        处理请求
        """
        try:
            ip_info = await parse_ip_info(request)
            ua_info = parse_user_agent_info(request)

            # 设置附加请求信息
            request.state.ip = ip_info.ip
            request.state.country = ip_info.country
            request.state.region = ip_info.region
            request.state.city = ip_info.city
            request.state.user_agent = ua_info.user_agent
            request.state.os = ua_info.os
            request.state.browser = ua_info.browser
            request.state.device = ua_info.device

            token = _request_ctx_var.set(request)
            return await call_next(request)
        finally:
            if token:
                _request_ctx_var.reset(token)
