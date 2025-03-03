# src/apps/v1/sys/crud/notification_rule.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/03/02
# @Author  : Aaron Zhou
# @File    : notification_rule.py
# @Software: Cursor
# @Description: 通知路由配置表CRUD类


from src.apps.v1.sys.models.mdl_notification_rule import (
    NotificationRule,
    NotificationRuleCreate,
    NotificationRuleUpdate,
)
from src.common.base_crud import CRUDBase


class CrudNotificationRule(CRUDBase):
    """通知规则配置表CRUD类"""
    def __init__(self):
        super().__init__(
            model=NotificationRule,
            create_model=NotificationRuleCreate,
            update_model=NotificationRuleUpdate,
        )


crud_notification_rule = CrudNotificationRule()
