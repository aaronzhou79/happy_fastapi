from typing import List, Sequence

from fastapi import APIRouter, Request

from src.apps.v1.sys.crud.permission_rule import crud_permission_rule
from src.apps.v1.sys.models.permission_rule import PermissionRule, PermissionRuleCreate, PermissionRuleUpdate
from src.core.conf import settings
from src.core.security.permission import require_permissions
from src.database.db_redis import redis_client
from src.database.db_session import async_audit_session, async_session

router = APIRouter(tags=["系统管理/权限规则"])


@router.post("/rules", response_model=PermissionRule)
@require_permissions("system:permission:rule:add")
async def create_rule(
    request: Request,
    *,
    obj_in: PermissionRuleCreate
) -> PermissionRule:
    """创建权限规则"""
    async with async_audit_session(async_session(), request=request) as session:
        rule = await crud_permission_rule.create(session=session, obj_in=obj_in)

    # 清除规则缓存
    await redis_client.delete(
        f"{settings.PERMISSION_RULES_REDIS_PREFIX}:{obj_in.permission_id}"
    )

    return rule

@router.put("/rules/{rule_id}", response_model=PermissionRule)
@require_permissions("system:permission:rule:edit")
async def update_rule(
    request: Request,
    *,
    obj_in: PermissionRuleUpdate
) -> PermissionRule:
    """更新权限规则"""
    async with async_audit_session(async_session(), request=request) as session:
        rule = await crud_permission_rule.update(
            session=session,
            obj_in=obj_in
        )

    # 清除规则缓存
    await redis_client.delete(
        f"{settings.PERMISSION_RULES_REDIS_PREFIX}:{obj_in.permission_id}"
    )

    return rule

@router.delete("/rules/{rule_id}")
@require_permissions("system:permission:rule:delete")
async def delete_rule(
    request: Request,
    *,
    rule_id: int
) -> None:
    """删除权限规则"""
    async with async_audit_session(async_session(), request=request) as session:
        rule = await crud_permission_rule.get_by_id(session=session, id=rule_id)
        if rule:
            await crud_permission_rule.delete(session=session, id=rule_id)
            # 清除规则缓存
            await redis_client.delete(
                f"{settings.PERMISSION_RULES_REDIS_PREFIX}:{rule.permission_id}"
            )

@router.get("/rules", response_model=List[PermissionRule])
@require_permissions("system:permission:rule:query")
async def get_rules(
    request: Request,
    *,
    permission_id: int | None = None
) -> Sequence[PermissionRule]:
    """获取权限规则列表"""
    async with async_audit_session(async_session(), request=request) as session:
        if permission_id:
            return await crud_permission_rule.get_by_permission(
                session=session,
                permission_id=permission_id
            )
        return await crud_permission_rule.get_multi(session=session)