
from typing import Annotated
from fastapi import Header
from src.apps.v1.demo.models.mdl_demo import Demo, DemoBase, DemoCreate, DemoUpdate
from src.apps.v1.demo.service.svr_demo import svr_demo
from src.common.base_api import BaseAPI
from src.core.context import set_tenant_id
from src.database.db_session import CurrentSession

demo_api = BaseAPI(
    module_name="demo",
    model=Demo,
    service=svr_demo,
    create_schema=DemoCreate,
    update_schema=DemoUpdate,
    base_schema=DemoBase,
    prefix="/demo",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=["功能调试"],
)


@demo_api.router.get(
    "/test",
    summary="测试",
    description="测试按租户ID进行分隔，需要在请求头中增加：X-Tenant-ID",
)
async def test(
    session: CurrentSession,
    id: int,
    x_tenant_id: Annotated[int, Header(..., description="租户ID")]
):
    """测试"""
    set_tenant_id(x_tenant_id)
    return await svr_demo.get_by_id(session=session, id=id)
