from typing import Sequence

from fastapi import APIRouter, Request

from src.apps.v1.sys.models.permission_rule import PermissionRule, PermissionRuleCreate, PermissionRuleUpdate
from src.apps.v1.sys.service.permission_rule import svr_permission_rule
from src.common.base_api import BaseAPI
from src.core.security.auth_security import DependsJwtAuth
from src.database.db_session import async_audit_session, async_session

router = APIRouter(tags=["系统管理/权限规则"])


permission_rule_api = BaseAPI(
    module_name="sys",
    model=PermissionRule,
    service=svr_permission_rule,
    create_schema=PermissionRuleCreate,
    update_schema=PermissionRuleUpdate,
    base_schema=PermissionRule,
    prefix="/perm_rule",
    gen_delete=True,
    tags=["系统管理/权限规则"],
)


@permission_rule_api.router.get(
    "/rules",
    dependencies=[
        DependsJwtAuth,
    ]
)
async def get_rules(
    request: Request,
    *,
    permission_id: int | None = None
) -> Sequence[PermissionRule]:
    """获取权限规则列表"""
    async with async_audit_session(async_session(), request=request) as session:
        if permission_id:
            return await svr_permission_rule.get_by_permission(
                session=session,
                permission_id=permission_id
            )
        return await svr_permission_rule.get_by_fields(session=session)