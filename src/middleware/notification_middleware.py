# src/middleware/notification_middleware.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Description: 通知中间件

import json

from functools import lru_cache
from typing import Any, Callable, Dict, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.apps.v1.sys.models.mdl_notification import NotificationCreate, NotificationType
from src.apps.v1.sys.service.svr_notification import svr_notification
from src.apps.v1.sys.sys_enums import NotificationCondition
from src.common.logger import log
from src.core.context import get_user_id
from src.database.db_session import async_audit_session, async_session


class NotificationMiddleware(BaseHTTPMiddleware):
    """通知中间件"""

    notification_rules: Dict[str, Dict[str, Any]] = {}

    def get_notification_rules(self) -> Dict[str, Dict[str, Any]]:
        """获取通知规则配置"""
        return self.notification_rules

    def __init__(
        self,
        app: ASGIApp,
    ):
        """
        初始化通知中间件

        :param app: ASGI应用
        :param notification_rules: 需要触发通知的路由配置
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

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求"""
        # 先执行后续中间件和路由处理
        response = await call_next(request)
        log.info(f"已加载 {len(self.get_notification_rules())} 条通知规则配置")

        # 检查是否需要发送通知
        await self._check_and_send_notification(request, response)

        return response

    async def _check_and_send_notification(
        self, request: Request, response: Response
    ) -> None:
        """检查并发送通知"""
        try:
            # 获取请求路径和方法
            path = request.url.path
            method = request.method

            # 检查是否匹配通知路由
            for route_path, config in self.notification_rules.items():
                if (
                    path.endswith(route_path)
                    and method.upper() == config.get("method", "").upper()
                ):
                    # 检查条件是否满足
                    condition = config.get("condition")
                    if condition and not self._check_condition(
                        condition, request, response
                    ):
                        continue

                    # 获取接收者ID
                    recipient_id = await self._get_recipient_id(
                        config.get("recipient_id_field"), request
                    )
                    if not recipient_id:
                        continue

                    # 创建通知
                    await self._create_notification(config, recipient_id, request)
        except Exception as e:
            log.error(f"通知中间件处理失败: {str(e)}")

    def _check_condition(
        self, condition: str, request: Request, response: Response
    ) -> bool:
        """检查条件是否满足"""
        try:
            # 这里可以根据需要实现更复杂的条件检查逻辑
            # 例如检查响应状态码、请求参数等
            # 总是触发
            if condition == NotificationCondition.ALWAYS:
                return True
            # 检查状态码范围
            is_success = 200 <= response.status_code < 300
            is_failure = 400 <= response.status_code < 600

            if condition == NotificationCondition.SUCCESS and is_success:
                return True

            if condition == NotificationCondition.FAILURE and is_failure:
                return True

        except Exception as e:
            log.error(f"检查通知条件失败: {str(getattr(e, 'data', e))}")

        return False

    async def _get_recipient_id(
        self, field_name: str | None, request: Request
    ) -> int | None:
        """获取接收者ID"""
        try:
            if not field_name:
                # 默认使用当前用户ID
                return get_user_id()

            # 1. 检查路径参数
            path_params = request.path_params
            if field_name in path_params:
                return int(str(path_params[field_name]))

            # 2. 检查查询参数
            query_params = request.query_params
            if field_name in query_params:
                return int(str(query_params[field_name]))

            # 3. 检查请求体（JSON）
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await request.json()
                    if isinstance(body, dict) and field_name in body:
                        return int(str(body[field_name]))
                except json.JSONDecodeError:
                    log.warning(f"请求体不是有效的JSON格式: {request.url.path}")

            # 4. 检查表单数据
            form_data = await request.form()
            if field_name in form_data:
                return int(str(form_data[field_name]))

            log.warning(
                f"未在请求中找到接收者ID字段 '{field_name}': {request.url.path}"
            )
        except Exception as e:
            log.error(f"获取接收者ID失败: {str(getattr(e, 'data', e))}")
        return None

    async def _create_notification(
        self, config: Dict[str, Any], recipient_id: int, request: Request
    ) -> None:
        """创建通知"""
        try:
            # 获取通知类型
            notification_type = getattr(
                NotificationType,
                config.get("type", "SYSTEM").upper(),
                NotificationType.SYSTEM,
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
                meta_data={"path": str(request.url.path), "method": request.method},
            )

            # 创建通知
            async with async_audit_session(async_session()) as session:
                await svr_notification.create(session=session, obj_in=notification)
        except Exception as e:
            log.error(f"创建通知失败: {str(getattr(e, 'data', e))}")
