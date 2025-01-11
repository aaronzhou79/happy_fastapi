from typing import Sequence

from fastapi import Request
from jose import jwt

from src.apps.v1.sys.service.permission import svr_permission
from src.core.conf import settings
from src.core.exceptions.errors import AuthorizationError
from src.core.security import auth_security
from src.database.db_redis import redis_client
from src.database.db_session import async_audit_session, async_session


class RequestPermission:
    """权限验证装饰器"""
    def __init__(self, permissions: str | Sequence[str], evaluate_rules: bool = True):
        if isinstance(permissions, str):
            permissions = [permissions]
        self.permissions = permissions
        self.evaluate_rules = evaluate_rules

    async def __call__(self, request: Request):
        """权限验证装饰器"""
        user = await auth_security.get_current_user(request)

        # 超级管理员跳过权限验证
        if user.is_superuser:
            return

        # 获取用户权限列表
        user_perms = await redis_client.get(
            f"{settings.JWT_PERMS_REDIS_PREFIX}:{request.user.user_data.id}"
        )
        if not user_perms:
            user_perms = []
            role_ids = [role.id for role in request.user.user_data.roles]
            async with async_session() as session:
                role_permissions = await svr_permission.get_role_permissions(
                    session=session,
                    role_id=role_ids
                )

                for perm in role_permissions:
                    if perm.perm_code:
                        user_perms.extend(perm.perm_code.split(","))

            if user_perms:
                await redis_client.setex(
                    f"{settings.JWT_PERMS_REDIS_PREFIX}:{request.user.user_data.id}",
                    settings.JWT_PERMS_REDIS_EXPIRE_SECONDS,
                    ",".join(set(user_perms))
                )
        else:
            user_perms = user_perms.split(",")

        # 验证权限
        for permission in self.permissions:
            if permission not in user_perms:
                raise AuthorizationError(msg=f"缺少权限: {permission}")


async def get_permission_id(perm: str) -> int | None:
    """根据权限标识获取权限ID"""
    from src.apps.v1.sys.crud.permission import crud_permission
    async with async_audit_session(async_session()) as session:
        permission = await crud_permission.get_by_fields(
            session=session,
            perms=perm
        )
        return permission[0].id if permission else None # type: ignore