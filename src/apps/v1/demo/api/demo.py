from typing import Annotated

from fastapi import Header
from sqlmodel import select

from src.apps.v1.demo.models import mdl_demo
from src.apps.v1.demo.models.mdl_demo import Demo, DemoBase, DemoCreate, DemoItem, DemoUpdate
from src.apps.v1.demo.service.svr_demo import svr_demo
from src.common.base_api import BaseAPI
from src.core.context import set_tenant_id
from src.core.responses.response_schema import ResponseModel, response_base
from src.database.db_session import CurrentSession


class UniqueConstraintViolationError(Exception):
    """唯一约束冲突异常"""
    pass


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


@demo_api.router.post(
    "/test2",
    summary="测试2",
    description="测试2",
)
async def test2(session: CurrentSession) -> ResponseModel:
    conflict_info = DemoItem.__unique_info__
    if conflict_info:
        await _check_unique_constraints(
            session,
            conflict_info,
            {"demo_id": 1, "product_name": "test", "product_code": "test"}
        )

    return response_base.success(data=conflict_info)


async def _check_unique_constraints(
    session: CurrentSession,
    unique_fields: list[dict],
    row_data: dict,
    model_class=DemoItem
) -> dict | None:
    """检查现有数据中的冲突"""
    import sqlalchemy as sa

    from sqlalchemy import text

    # 检查是否有唯一约束字段存在于行数据中
    has_unique_fields = False
    for field in unique_fields:
        for column in field.get("columns", []):
            if column in row_data:
                has_unique_fields = True
                break
        if has_unique_fields:
            break

    if not has_unique_fields:
        return None

    # 构建原始SQL查询，确保正确的括号和优先级
    table_name = model_class.__tablename__
    sql_parts = []
    params = {}
    param_index = 1

    for field in unique_fields:
        field_conditions = []
        field_has_data = False

        for column in field.get("columns", []):
            if column in row_data:
                param_name = f"{column}_{param_index}"
                field_conditions.append(f"{table_name}.{column} = :{param_name}")
                params[param_name] = row_data[column]
                field_has_data = True
                param_index += 1

        if field_has_data and field_conditions:
            sql_parts.append(f"({' AND '.join(field_conditions)})")

    if not sql_parts:
        return None

    # 构建完整的SQL查询
    sql_query = f"SELECT {table_name}.id FROM {table_name} WHERE {' OR '.join(sql_parts)}"

    # 执行查询
    result = await session.execute(text(sql_query), params)
    existing_records = result.scalars().all()

    if not existing_records:
        return None
    elif len(existing_records) > 1:
        # 处理多条记录的情况
        unique_field_names = [", ".join(field.get("columns", [])) for field in unique_fields]
        raise UniqueConstraintViolationError(f"找到多条记录，违反唯一约束: {', '.join(unique_field_names)}")
    elif existing_records:
        # 处理找到一条记录的情况
        unique_field_names = [", ".join(field.get("columns", [])) for field in unique_fields]
        return {
            'error_message': f'数据已存在，违反唯一约束: {", ".join(unique_field_names)}'
        }

    return None


