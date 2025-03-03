
from typing import Literal

import sqlalchemy as sa

from sqlmodel import Field, SQLModel

from src.apps.v1.sys.sys_enums import NotificationCondition, NotificationType
from src.common.base_models.database_mixin import DatabaseModel


class NotificationRuleBase(SQLModel):
    """通知规则配置表"""

    path: str = Field(..., description="API路径")
    method: str = Field(..., description="HTTP方法")
    type: NotificationType = Field(..., nullable=False, description="通知类型")
    title_template: str = Field(..., nullable=False, description="通知标题模板")
    content_template: str = Field(..., nullable=False, description="通知内容模板")
    condition: NotificationCondition = Field(
        default=NotificationCondition.SUCCESS,
        description="触发条件"
    )
    recipient_id_field: str | None = Field(
        default=None,
        description="接收者ID字段"
    )


class NotificationRule(NotificationRuleBase, DatabaseModel, table=True):
    """通知规则配置表"""
    __tablename__: Literal["sys_notification_rules"] = "sys_notification_rules"
    __table_args__ = (
        sa.UniqueConstraint('path', 'method', 'type', name='uq_notification_rule_path_method_type'),
        {
            "comment": "通知规则配置表",
        }
    )


class NotificationRuleCreate(NotificationRuleBase):
    """通知规则配置表创建"""


class NotificationRuleUpdate(NotificationRuleBase):
    """通知规则配置表更新"""
    id: int = Field(..., description="ID")


class NotificationRuleGet(NotificationRuleBase):
    """通知规则配置表"""
    id: int = Field(..., description="ID")

