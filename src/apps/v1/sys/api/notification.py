# src/apps/v1/sys/api/notification.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/02/27
# @Author  : Aaron Zhou
# @File    : notification.py
# @Software: Cursor
# @Description: 通知管理API
from src.apps.v1.sys.models.mdl_notification import (
    Notification,
    NotificationBase,
    NotificationCreate,
    NotificationUpdate,
)
from src.apps.v1.sys.service.svr_notification import svr_notification
from src.common.base_api import BaseAPI
from src.core.responses.response_schema import ResponseModel, response_base
from src.database.db_session import CurrentSession

notification_api = BaseAPI(
    module_name="sys",
    model=Notification,
    service=svr_notification,
    create_schema=NotificationCreate,
    update_schema=NotificationUpdate,
    base_schema=NotificationBase,
    prefix="/notification",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=["系统管理/通知管理"],
)


@notification_api.router.get("/user/{user_id}")
async def get_user_notifications(
    user_id: int,
    db: CurrentSession,
) -> ResponseModel:
    """获取用户通知"""
    data = await svr_notification.get_by_user(user_id=user_id)
    return response_base.success(data=data)
