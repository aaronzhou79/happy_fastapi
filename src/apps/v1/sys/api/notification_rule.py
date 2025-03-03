# src/apps/v1/sys/api/notification_rule.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : notification_rule.py
# @Software: Cursor
# @Description: 角色管理API
from src.apps.v1.sys.models.mdl_notification_rule import (
    NotificationRule,
    NotificationRuleBase,
    NotificationRuleCreate,
    NotificationRuleUpdate,
)
from src.apps.v1.sys.service.svr_notification_rule import svr_notification_rule
from src.apps.v1.sys.sys_enums import NotificationCondition, NotificationType
from src.common.base_api import BaseAPI
from src.core.responses.response_schema import ResponseModel, response_base
from src.database.db_session import async_audit_session, async_session

notification_rule_api = BaseAPI(
    module_name="sys",
    model=NotificationRule,
    service=svr_notification_rule,
    create_schema=NotificationRuleCreate,
    update_schema=NotificationRuleUpdate,
    base_schema=NotificationRuleBase,
    prefix="/notification_rule",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=["系统管理/通知规则管理"],
)


@notification_rule_api.router.post("/init")
async def init_notification_rule(
) -> ResponseModel:
    """初始化通知规则"""
    hardcoded_rules = {
        "/user/create": {
            "method": "POST",
            "type": "SYSTEM",
            "title_template": "用户创建通知",
            "content_template": "新用户已创建",
            "condition": "success"
        },
        # 可以添加更多硬编码的规则
    }

    async with async_audit_session(async_session()) as session:
        # 检查是否已存在数据
        existing_rules = await svr_notification_rule.get_all_notification_rules(session)

        if existing_rules:
            return response_base.fail(data=f"数据库中已存在 {len(existing_rules)} 条通知规则配置，跳过迁移")

        # 插入硬编码的规则配置
        for path, config in hardcoded_rules.items():
            rule = NotificationRuleCreate(
                path=path,
                method=config["method"],
                type=NotificationType(config["type"]),
                title_template=config["title_template"],
                content_template=config["content_template"],
                condition=NotificationCondition(config["condition"]),
                recipient_id_field=config.get("recipient_id_field")
            )
            await svr_notification_rule.create(session, rule)

    return response_base.success(data=f"成功迁移 {len(hardcoded_rules)} 条通知规则配置到数据库，重启服务后生效！")
