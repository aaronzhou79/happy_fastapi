# src/apps/v1/sys/api/dept.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : dept.py
# @Software: Cursor
# @Description: 用户管理API

import asyncio

from fastapi import Request

from src.apps.v1.sys.models import Dept, DeptSchemaBase, DeptSchemaCreate, DeptSchemaUpdate, DeptSchemaWithUsers
from src.common.base_api import BaseAPI
from src.core.responses.response import response_base
from src.core.responses.response_schema import ResponseModel
from src.database.db_session import CurrentSession, async_audit_session, async_session

dept_api = BaseAPI(
    model=Dept,
    create_schema=DeptSchemaCreate,
    update_schema=DeptSchemaUpdate,
    base_schema=DeptSchemaBase,
    with_schema=DeptSchemaWithUsers,
    prefix="/dept",
    gen_delete=True,
    gen_bulk_create=True,
    tags=["部门管理"],
)


@dept_api.router.post("/lock_test")
async def lock_test(
    session: CurrentSession,
    request: Request,
    dept_id: int,
    name: str
) -> ResponseModel:
    """
    测试锁。
    """
    model = await Dept.get_by_id(session, id=dept_id)
    if not model:
        return response_base.fail(data="部门不存在")

    async def do_something() -> str:
        await asyncio.sleep(30)
        return "done"
    # 使用 with_lock 执行自定义操作
    await model.with_lock(lambda: do_something())

    # update 和 delete 方法已经内置了锁保护
    async with async_audit_session(async_session(), request) as session:
        data = await model.update(session=session, id=model.id, name=name)
    return response_base.success(data=data)


@dept_api.router.get("/cache_get")
async def cache_get(
) -> ResponseModel:
    data = await dept_api.cache_manager.get("test")
    return response_base.success(data=data)


@dept_api.router.get("/cache_set")
async def cache_set(
) -> ResponseModel:
    data = await dept_api.cache_manager.set("test", "test")
    return response_base.success(data=data)
