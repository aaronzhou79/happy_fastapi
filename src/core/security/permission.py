from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Sequence
from fastapi import Request
from src.core.exceptions.errors import AuthorizationError
from src.core.security.rule_engine import RuleEngine
from src.database.db_redis import redis_client
from src.core.conf import settings
from src.database.db_session import async_audit_session, async_session

def require_permissions(
    permissions: str | Sequence[str],
    evaluate_rules: bool = True
) -> Callable:
    """
    权限验证装饰器

    Args:
        permissions: 所需权限标识或权限标识列表
        evaluate_rules: 是否评估动态规则
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args: Any, **kwargs: Any) -> Any:
            # request = next((arg for arg in args if isinstance(arg, Request)), None)
            if not request:
                raise AuthorizationError(msg="无法获取请求上下文")

            if not hasattr(request, "user"):
                raise AuthorizationError(msg="用户未登录")

            # 超级管理员跳过权限验证
            if request.user.user_data.is_superuser:
                return await func(*args, **kwargs)

            # 获取用户权限列表(优先从缓存获取)
            user_perms = await redis_client.get(
                f"{settings.JWT_PERMS_REDIS_PREFIX}:{request.user.user_data.id}"
            )

            if not user_perms:
                # 从数据库获取权限
                user_perms = []
                for role in request.user.user_data.roles:
                    for perm in role.permissions:
                        if perm.perms:
                            user_perms.extend(perm.perms.split(","))

                # 缓存权限列表
                if user_perms:
                    await redis_client.setex(
                        f"{settings.JWT_PERMS_REDIS_PREFIX}:{request.user.user_data.id}",
                        settings.JWT_PERMS_REDIS_EXPIRE_SECONDS,
                        ",".join(set(user_perms))
                    )
            else:
                user_perms = user_perms.split(",")

            # 验证基本权限
            required_perms = [permissions] if isinstance(permissions, str) else permissions
            if not any(perm in user_perms for perm in required_perms):
                raise AuthorizationError(msg="权限不足")

            # 验证动态规则
            if evaluate_rules:
                context = {
                    "user": request.user.user_data,
                    "ip": request.state.ip,
                    "current_time": datetime.now(),
                    "data": kwargs
                }

                # 获取并评估所有相关权限的规则
                for perm in required_perms:
                    permission_id = await get_permission_id(perm)
                    if permission_id:
                        rules = await RuleEngine.get_permission_rules(permission_id)
                        for rule in rules:
                            if not await RuleEngine.evaluate_rule(rule, context):
                                raise AuthorizationError(msg="不满足权限规则要求")

            return await func(*args, **kwargs)
        return wrapper
    return decorator

async def get_permission_id(perm: str) -> int | None:
    """根据权限标识获取权限ID"""
    from src.apps.v1.sys.crud.permission import crud_permission
    async with async_audit_session(async_session()) as session:
        permission = await crud_permission.get_by_fields(
            session=session,
            perms=perm
        )
        return permission[0].id if permission else None # type: ignore