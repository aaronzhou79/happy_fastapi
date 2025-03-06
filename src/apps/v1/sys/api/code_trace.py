# src/apps/v1/sys/api/code_trace.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025/02/23
# @Author  : Aaron Zhou
# @File    : code_trace.py
# @Software: Cursor
# @Description: 编码跟踪API

from fastapi import Query, Request

from src.apps.v1.sys.models.mdl_code_trace import (
    CodeTrace,
    CodeTraceBase,
    CodeTraceCreate,
    CodeTraceUpdate,
)
from src.apps.v1.sys.service.svr_code_trace import svr_code_trace
from src.common.base_api import BaseAPI
from src.common.enums import DocumentType
from src.core.responses.response_schema import ResponseModel, response_base
from src.core.security.auth_security import DependsJwtAuth
from src.database.db_session import async_audit_session, async_session

code_trace_api = BaseAPI(
    module_name="sys",
    model=CodeTrace,
    service=svr_code_trace,
    create_schema=CodeTraceCreate,
    update_schema=CodeTraceUpdate,
    base_schema=CodeTraceBase,
    gen_create=False,
    gen_delete=False,
    gen_update=False,
    prefix="/code_trace",
    tags=["系统管理/编码生成"],
)


@code_trace_api.router.get(
    "/get_code",
    summary="获取编码",
    description="每次调用，都会返回一个新的编码，需要前端处理，在页面加载时调用并保存到LocalStorage中，保存或关闭后，需要手工清理LocalStorage!",
    dependencies=[DependsJwtAuth],
)
async def get_next_code(
    request: Request,
    doc_type: DocumentType,
    classify_code: str | None = Query(
        default=None, description="分类编码(用于在前缀和流水号之间插入字符)"
    ),
) -> ResponseModel:
    """获取下一个编码"""
    async with async_audit_session(async_session(), request) as db:
        code = await svr_code_trace.get_next_code(db, doc_type, classify_code)
    return response_base.success(data={"doc_type": doc_type, "code": code})
