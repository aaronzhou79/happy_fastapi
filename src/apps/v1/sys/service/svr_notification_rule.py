# src/apps/v1/sys/service/svr_notification_rule.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/03/02
# @Author  : Aaron Zhou
# @File    : svr_notification_rule.py
# @Software: Cursor
# @Description: 通知路由配置表服务


from typing import Any

from src.apps.v1.sys.crud.crud_notification_rule import crud_notification_rule
from src.apps.v1.sys.models.mdl_notification_rule import (
    NotificationRule,
    NotificationRuleCreate,
    NotificationRuleGet,
    NotificationRuleUpdate,
)
from src.common.base_service import BaseService
from src.database.db_session import AuditAsyncSession


class SvrNotificationRule(
    BaseService[NotificationRule, NotificationRuleCreate, NotificationRuleUpdate]
):
    """
    通知规则配置表服务
    """

    def __init__(self):
        self.crud = crud_notification_rule

    async def get_all_notification_rules(
        self, db: AuditAsyncSession
    ) -> list[NotificationRuleGet]:
        """获取所有通知规则配置"""
        rules = await self.crud.get_multi(db)
        return [NotificationRuleGet.model_validate(rule) for rule in rules]

    async def format_notification_rules(
        self, rules: list[NotificationRuleGet]
    ) -> dict[str, dict[str, Any]]:
        """将通知规则列表转换为中间件所需的格式"""
        formatted_rules = {}

        for rule in rules:
            formatted_rules[rule.path] = {
                "method": rule.method,
                "type": rule.type,
                "title_template": rule.title_template,
                "content_template": rule.content_template,
                "condition": rule.condition,
            }

        return formatted_rules


svr_notification_rule = SvrNotificationRule()
