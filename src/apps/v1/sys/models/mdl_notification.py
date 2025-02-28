# src/apps/v1/sys/models/mdl_notification.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Description: 通知模型

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

import sqlalchemy as sa

from sqlmodel import Field, SQLModel

from src.common.base_models.database_mixin import DatabaseModel
from src.common.base_models.datetime_mixin import DateTimeMixin
from src.common.base_models.tenant_mixin import TenantMixin
from src.common.enums import StrEnum


class NotificationType(StrEnum):
    """通知类型"""
    SYSTEM = "system"  # 系统通知
    USER = "user"      # 用户通知
    TASK = "task"      # 任务通知
    ALERT = "alert"    # 警报通知


class NotificationStatus(StrEnum):
    """通知状态"""
    UNREAD = "unread"  # 未读
    READ = "read"      # 已读


class NotificationBase(SQLModel):
    """通知基础模型"""
    title: str = Field(..., description="通知标题")
    content: str = Field(..., description="通知内容")
    type: NotificationType = Field(default=NotificationType.SYSTEM, description="通知类型")
    status: NotificationStatus = Field(default=NotificationStatus.UNREAD, description="通知状态")
    recipient_id: str = Field(..., description="接收者ID")
    sender_id: str | None = Field(default=None, description="发送者ID")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    read_at: datetime | None = Field(default=None, description="阅读时间")
    meta_data: dict[str, Any] | None = Field(default=None, sa_type=sa.JSON, description="元数据")


class Notification(NotificationBase, TenantMixin, DateTimeMixin, DatabaseModel, table=True):
    """通知模型"""
    __tablename__: Literal["notification"] = "notification"


class NotificationCreate(NotificationBase):
    """创建通知请求模型"""


class NotificationUpdate(NotificationBase):
    """更新通知请求模型"""
    id: str = Field(..., description="通知ID")

