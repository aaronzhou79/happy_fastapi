# src/apps/v1/sys/api/notification.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/02/27
# @Author  : Aaron Zhou
# @File    : notification.py
# @Software: Cursor
# @Description: 通知管理API
from fastapi import Request

from src.apps.v1.sys.models.mdl_notification import (
    Notification,
    NotificationBase,
    NotificationCreate,
    NotificationUpdate,
)
from src.apps.v1.sys.service.svr_notification import svr_notification
from src.common.base_api import BaseAPI
from src.core.responses.response_schema import ResponseModel, response_base
from src.database.db_session import async_audit_session, async_session

notification_api = BaseAPI(
    module_name="sys",
    model=Notification,
    service=svr_notification,
    create_schema=NotificationCreate,
    update_schema=NotificationUpdate,
    base_schema=NotificationBase,
    prefix="/notification",
    gen_bulk_create=False,
    gen_bulk_delete=False,
    gen_update=False,
    gen_delete=True,
    tags=["系统管理/通知管理"],
)


@notification_api.router.get(
    "/user/{user_id}",
    summary="获取用户通知",
)
async def get_user_notifications(
    user_id: int,
) -> ResponseModel:
    """获取用户通知"""
    data = await svr_notification.get_by_user(user_id=user_id)
    return response_base.success(data=data)


@notification_api.router.post(
    "/{notification_id}/read",
    summary="标记通知为已读",
)
async def mark_notification_as_read(
    notification_id: int,
    request: Request,
) -> ResponseModel:
    """标记通知为已读"""
    async with async_audit_session(async_session(), request) as db:
        data = await svr_notification.mark_as_read(db, notification_id=notification_id)
    return response_base.success(data=data)


@notification_api.router.post(
    "/user/{user_id}/read_all",
    summary="标记用户所有通知为已读",
)
async def mark_all_notifications_as_read(
    user_id: int,
    request: Request,
) -> ResponseModel:
    """标记用户所有通知为已读"""
    async with async_audit_session(async_session(), request) as db:
        data = await svr_notification.mark_all_as_read(db, user_id=user_id)
    return response_base.success(data=data)


@notification_api.router.get(
    "/user/{user_id}/unread_count",
    summary="获取用户未读通知数量",
)
async def get_unread_notification_count(
    user_id: int,
) -> ResponseModel:
    """获取用户未读通知数量"""
    data = await svr_notification.get_unread_count(user_id=user_id)
    return response_base.success(data=data)
