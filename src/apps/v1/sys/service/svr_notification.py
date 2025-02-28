# src/apps/v1/sys/service/svr_notification.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/02/27
# @Author  : Aaron Zhou
# @File    : svr_notification.py
# @Software: Cursor
# @Description: 通知服务


from src.apps.v1.sys.crud.crud_notification import crud_notification
from src.apps.v1.sys.models.mdl_notification import Notification, NotificationCreate, NotificationUpdate
from src.common.base_crud import HookContext
from src.common.base_service import BaseService
from src.common.enums import HookTypeEnum
from src.database.db_redis import redis_client
from src.database.db_session import AuditAsyncSession


class SvrNotification(BaseService[Notification, NotificationCreate, NotificationUpdate]):
    """
    通知服务
    """
    # Redis键前缀
    NOTIFICATION_KEY_PREFIX = "notification:"
    USER_NOTIFICATIONS_KEY = "user_notifications:"

    def __init__(self):
        self.crud = crud_notification
        self.crud.hook_manager.add_hook(
            hook_type=HookTypeEnum.after_create,
            func=self._after_create,
            priority=1
        )

    async def _after_create(self, context: HookContext) -> str:
        """创建后处理"""
        db_obj = context.params['db_obj']
        # 将通知存储到Redis
        notification_key = f"{self.NOTIFICATION_KEY_PREFIX}{db_obj.id}"
        user_notifications_key = f"{self.USER_NOTIFICATIONS_KEY}{db_obj.recipient_id}"

        try:
            # 存储通知详情
            await redis_client.set(
                notification_key,
                db_obj.model_dump_json(),
                ex=60 * 60 * 24 * 30  # 30天过期
            )

            # 将通知ID添加到用户的通知列表
            redis_client.lpush(user_notifications_key, db_obj.id)

            # 设置用户通知列表的过期时间
            await redis_client.expire(
                user_notifications_key,
                60 * 60 * 24 * 30  # 30天过期
            )
        except Exception as e:
            raise e from e

        return f"通知创建成功: {db_obj.id}"

    async def get_notification(self, notification_id: str) -> Notification | None:
        """获取通知详情"""
        notification_key = f"{self.NOTIFICATION_KEY_PREFIX}{notification_id}"

        try:
            notification_data = await redis_client.get(notification_key)
            if not notification_data:
                return None

            return Notification.model_validate_json(notification_data)
        except Exception as e:
            raise e from e

    async def get_by_user(
        self,
        db: AuditAsyncSession,
        user_id: int
    ) -> list[Notification]:
        """获取用户通知"""
        user_notifications_key = f"{self.USER_NOTIFICATIONS_KEY}{user_id}"

        # 直接使用 execute_command 方法执行 LRANGE 命令
        notification_ids = await redis_client.execute_command('LRANGE', user_notifications_key, 0, -1) or []

        # 获取通知详情
        notifications = []
        for notification_id in notification_ids:
            notification = await self.get_notification(notification_id)
            if notification:
                notifications.append(notification)

        return notifications


svr_notification = SvrNotification()
