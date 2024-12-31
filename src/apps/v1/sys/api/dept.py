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

from src.common.base_api import BaseAPI
from src.core.responses.response import response_base
from src.database.db_session import async_audit_session, async_session

from ..model.depts import Department, DepartmentCreate, DepartmentUpdate

dept_api = BaseAPI(
    model=Department,
    create_schema=DepartmentCreate,
    update_schema=DepartmentUpdate,
    prefix="/dept",
    gen_delete=True,
    tags=["部门管理"],
)


@dept_api.router.post("/lock_test")
async def lock_test(
    request: Request,
    dept_id: int,
    name: str
):
    model = await Department.get_by_id(dept_id)
    if not model:
        return response_base.fail(data="部门不存在")

    async def do_something():
        await asyncio.sleep(30)
        return "done"
    # 使用 with_lock 执行自定义操作
    await model.with_lock(lambda: do_something())

    # update 和 delete 方法已经内置了锁保护
    async with async_audit_session(async_session(), request) as session:
        data = await model.update(session=session, pk=model.id, name=name)
    return response_base.success(data=data)
