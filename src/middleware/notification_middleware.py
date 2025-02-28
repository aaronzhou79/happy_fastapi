# src/middleware/notification_middleware.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Description: 通知中间件

import json

from typing import Any, Callable, Dict, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.apps.v1.sys.models.mdl_notification import NotificationCreate, NotificationType
from src.apps.v1.sys.service.svr_notification import svr_notification
from src.common.logger import log
from src.core.context import get_user_id
from src.database.db_session import async_audit_session, async_session


class NotificationMiddleware(BaseHTTPMiddleware):
    """通知中间件"""

    def __init__(
        self,
        app: ASGIApp,
        notification_routes: Dict[str, Dict[str, Any]] | None = None
    ):
        """
        初始化通知中间件

        :param app: ASGI应用
        :param notification_routes: 需要触发通知的路由配置
            格式: {
                "路由路径": {
                    "method": "请求方法",
                    "type": "通知类型",
                    "title_template": "通知标题模板",
                    "content_template": "通知内容模板",
                    "recipient_id_field": "接收者ID字段",
                    "condition": "触发条件"
                }
            }
        """
        super().__init__(app)
        self.notification_routes = notification_routes or {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        # 先执行后续中间件和路由处理
        response = await call_next(request)

        # 检查是否需要发送通知
        await self._check_and_send_notification(request, response)

        return response

    async def _check_and_send_notification(self, request: Request, response: Response) -> None:
        """检查并发送通知"""
        try:
            # 获取请求路径和方法
            path = request.url.path
            method = request.method

            # 检查是否匹配通知路由
            for route_path, config in self.notification_routes.items():
                if path.endswith(route_path) and method.upper() == config.get("method", "").upper():
                    # 检查条件是否满足
                    condition = config.get("condition")
                    if condition and not self._check_condition(condition, request, response):
                        continue

                    # 获取接收者ID
                    recipient_id = self._get_recipient_id(config.get("recipient_id_field"), request)
                    if not recipient_id:
                        continue

                    # 创建通知
                    await self._create_notification(config, recipient_id, request)
        except Exception as e:
            log.error(f"通知中间件处理失败: {str(e)}")

    def _check_condition(self, condition: str, request: Request, response: Response) -> bool:
        """检查条件是否满足"""
        try:
            # 这里可以根据需要实现更复杂的条件检查逻辑
            # 例如检查响应状态码、请求参数等
            if condition == "success" and 200 <= response.status_code < 300:
                return True
        except Exception as e:
            log.error(f"检查通知条件失败: {str(getattr(e, 'data', e))}")

        return False

    def _get_recipient_id(self, field_name: str | None, request: Request) -> int | None:
        """获取接收者ID"""
        try:
            if not field_name:
                # 默认使用当前用户ID
                return get_user_id()

            # 从请求中获取指定字段
            # 这里可以根据需要实现更复杂的获取逻辑
            # 例如从请求体、URL参数、路径参数等获取
        except Exception as e:
            log.error(f"获取接收者ID失败: {str(getattr(e, 'data', e))}")
        return None

    async def _create_notification(
        self,
        config: Dict[str, Any],
        recipient_id: int,
        request: Request
    ) -> None:
        """创建通知"""
        try:
            # 获取通知类型
            notification_type = getattr(
                NotificationType,
                config.get("type", "SYSTEM").upper(),
                NotificationType.SYSTEM
            )

            # 获取通知标题和内容
            title = config.get("title_template", "系统通知")
            content = config.get("content_template", "您有一条新的系统通知")

            # 创建通知
            notification = NotificationCreate(
                title=title,
                content=content,
                type=notification_type,
                recipient_id=recipient_id,
                sender_id=get_user_id(),
                meta_data={"path": str(request.url.path), "method": request.method}
            )

            # 创建通知
            async with async_audit_session(async_session()) as session:
                await svr_notification.create(session=session, obj_in=notification)
        except Exception as e:
            log.error(f"创建通知失败: {str(getattr(e, 'data', e))}")