# src/apps/v1/sys/crud/crud_notification.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : role.py
# @Software: Cursor
# @Description: 通知相关CRUD类

from src.apps.v1.sys.models.mdl_notification import Notification, NotificationCreate, NotificationUpdate
from src.common.base_crud import CRUDBase


class CrudNotification(CRUDBase):
    """通知相关CRUD类"""
    def __init__(self):
        super().__init__(
            model=Notification,
            create_model=NotificationCreate,
            update_model=NotificationUpdate,
        )


crud_notification = CrudNotification()
