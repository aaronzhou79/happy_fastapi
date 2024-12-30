from typing import Annotated

from fastapi import APIRouter, Query

from src.common.data_model.base_model import AuditLog
from src.common.data_model.query_fields import QueryOptions
from src.core.responses.response import response_base

router = APIRouter(prefix="/audit_log")

@router.post("/query")
async def query(
    options: QueryOptions
):
    items, total = await AuditLog.query_with_count(options=options)
    return response_base.success(data={"total": total, "items": items})

@router.get("/get_all")
async def get_all(
    include_deleted: Annotated[bool, Query(...)] = False
):
    logs: list[AuditLog] = await AuditLog.get_all(include_deleted=include_deleted)
    data = [await log.to_dict() for log in logs]
    return response_base.success(data=data)