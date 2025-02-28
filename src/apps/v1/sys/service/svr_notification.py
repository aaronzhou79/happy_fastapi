# src/apps/v1/sys/service/svr_notification.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/02/27
# @Author  : Aaron Zhou
# @File    : svr_notification.py
# @Software: Cursor
# @Description: 通知服务


from src.apps.v1.sys.crud.crud_notification import crud_notification
from src.apps.v1.sys.models.mdl_notification import (
    Notification,
    NotificationCreate,
    NotificationList,
    NotificationStatus,
    NotificationUpdate,
)
from src.common.base_crud import HookContext
from src.common.base_service import BaseService
from src.common.enums import HookTypeEnum
from src.core.context import get_user_id
from src.core.exceptions import errors
from src.database.db_redis import redis_client
from src.database.db_session import AuditAsyncSession, async_session
from src.utils.timezone import TimeZone


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
        self.crud.hook_manager.add_hook(
            hook_type=HookTypeEnum.before_delete,
            func=self._before_delete,
            priority=1
        )
        self.crud.hook_manager.add_hook(
            hook_type=HookTypeEnum.after_delete,
            func=self._after_delete,
            priority=1
        )

    async def _before_delete(self, context: HookContext) -> bool:
        """删除前处理"""
        db_obj = context.params['db_obj']
        # 从Redis中删除通知
        try:
            # 获取通知详情
            notification = await self.get_notification(notification_id=db_obj.id)
            if not notification:
                return False

            # 从用户通知列表中删除通知ID
            if get_user_id() != notification.recipient_id:
                raise errors.RequestError(data="只能删除自己的通知！")  # noqa: TRY301
        except Exception as e:
            raise errors.RequestError(data=f"删除通知失败: {str(getattr(e, 'data', e))}") from e

        return True

    async def _after_delete(self, context: HookContext) -> bool:
        """删除后处理"""
        db_obj = context.params['db_obj']
        # 从Redis中删除通知
        notification_key = f"{self.NOTIFICATION_KEY_PREFIX}{db_obj.id}"
        try:
            # 获取通知详情
            notification = await self.get_notification(notification_id=db_obj.id)
            if not notification:
                return False

            # 从Redis中删除通知
            await redis_client.delete(notification_key)

            # 从用户通知列表中删除通知ID
            user_notifications_key = f"{self.USER_NOTIFICATIONS_KEY}{notification.recipient_id}"
            await redis_client.lrem(user_notifications_key, 0, notification.id)  # type: ignore

        except Exception as e:
            raise errors.RequestError(data=f"删除通知失败: {str(getattr(e, 'data', e))}") from e

        return True

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
            await redis_client.lpush(user_notifications_key, db_obj.id)   # type: ignore

            # 设置用户通知列表的过期时间
            await redis_client.expire(
                user_notifications_key,
                60 * 60 * 24 * 30  # 30天过期
            )
        except Exception as e:
            raise e from e

        return f"通知创建成功: {db_obj.id}"

    async def get_notification(self, notification_id: int) -> Notification | None:
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
        user_id: int
    ) -> NotificationList:
        """获取用户通知"""
        user_notifications_key = f"{self.USER_NOTIFICATIONS_KEY}{user_id}"

        # 直接使用 execute_command 方法执行 LRANGE 命令
        # notification_ids = await redis_client.execute_command('LRANGE', user_notifications_key, 0, -1) or []
        notification_ids = await redis_client.lrange(user_notifications_key, 0, -1)  # type: ignore

        # 获取用户通知列表的总数量
        total_count = await redis_client.llen(user_notifications_key)  # type: ignore

        # 获取通知详情
        notifications = []
        for notification_id in notification_ids:
            notification = await self.get_notification(notification_id)
            if notification:
                notifications.append(notification)

        return NotificationList(
            total=total_count,
            items=notifications
        )

    async def get_unread_count(self, user_id: int) -> int:
        """获取用户未读通知数量"""
        user_notifications_key = f"{self.USER_NOTIFICATIONS_KEY}{user_id}"

        try:
            # 获取用户所有通知ID
            notification_ids = await redis_client.lrange(user_notifications_key, 0, -1)  # type: ignore

            # 统计未读通知数量
            unread_count = 0
            for notification_id in notification_ids:
                notification = await self.get_notification(notification_id=int(notification_id))  # type: ignore
                if notification and notification.status == NotificationStatus.UNREAD:
                    unread_count += 1
        except Exception as e:
            raise errors.RequestError(data=f"获取未读通知数量失败: {str(getattr(e, 'data', e))}") from e

        return unread_count

    async def mark_as_read(self, session: AuditAsyncSession, notification_id: int) -> bool:
        """标记通知为已读"""
        try:
            notification = await self.get_notification(notification_id)
            if not notification:
                return False

            notification.status = NotificationStatus.READ
            notification.read_at = TimeZone.now()

            notification_key = f"{self.NOTIFICATION_KEY_PREFIX}{notification_id}"
            await redis_client.set(
                notification_key,
                notification.model_dump_json(),
                ex=60 * 60 * 24 * 30  # 30天过期
            )

            # 同步到数据库
            await self.crud.update(
                session=session,
                obj_in=notification,
            )

        except Exception as e:
            raise errors.RequestError(data=f"标记通知为已读失败: {str(getattr(e, 'data', e))}") from e

        return True

    async def mark_all_as_read(self, session: AuditAsyncSession, user_id: int) -> bool:
        """标记用户所有通知为已读"""
        user_notifications_key = f"{self.USER_NOTIFICATIONS_KEY}{user_id}"

        try:
            # 获取用户所有通知ID
            notification_ids = await redis_client.lrange(user_notifications_key, 0, -1)  # type: ignore

            # 标记所有通知为已读
            for notification_id in notification_ids:
                await self.mark_as_read(session, notification_id=int(notification_id))

        except Exception as e:
            raise errors.RequestError(data=f"标记所有通知为已读失败: {str(getattr(e, 'data', e))}") from e

        return True


svr_notification = SvrNotification()
