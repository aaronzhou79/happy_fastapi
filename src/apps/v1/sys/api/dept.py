# src/apps/v1/sys/api/dept.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : dept.py
# @Software: Cursor
# @Description: 用户管理API

import asyncio

from typing import Annotated

from fastapi import APIRouter, Query, Request

from src.common.data_model.query_fields import QueryOptions
from src.core.responses.response import response_base
from src.database.db_session import async_audit_session, async_session

from ..model import Department, DepartmentCreate, DepartmentList, DepartmentUpdate

router = APIRouter(prefix="/dept")

@router.post("/lock_test")
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

@router.post("/create")
async def create(
    request: Request,
    dept: DepartmentCreate  # type: ignore
):
    async with async_audit_session(async_session(), request) as session:
        data = await Department.create(session=session, **dept.model_dump())

    return response_base.success(data=data)


@router.put("/update")
async def update(
    request: Request,
    dept_id: int,
    dept_update: DepartmentUpdate  # type: ignore
):
    async with async_audit_session(async_session(), request) as session:
        data = await Department.update(session=session, pk=dept_id, **dept_update.model_dump())

    return response_base.success(data=data)

@router.delete("/delete")
async def delete(
    request: Request,
    dept_id: int
):
    async with async_audit_session(async_session(), request) as session:
        await Department.delete(session=session, pk=dept_id)
    return response_base.success(data="部门删除成功")

@router.get("/get")
async def get(
    dept_id: int,
    max_depth: int = 2
):
    dept = await Department.get_by_id(dept_id)
    if not dept:
        return response_base.fail(data="部门不存在")
    data = await dept.to_api_dict(max_depth=max_depth)
    return response_base.success(data=data)

@router.post("/query")
async def query(
    options: QueryOptions
):
    items, total = await Department.query_with_count(options=options)
    return response_base.success(data={"total": total, "items": items})

@router.get("/get_all")
async def get_all(
    include_deleted: Annotated[bool, Query(...)] = False
):
    depts: list[Department] = await Department.get_all(include_deleted=include_deleted)
    data = DepartmentList(items=depts)
    return response_base.success(data=data)
