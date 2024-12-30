# src/apps/v1/sys/api/user.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Data    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : user.py
# @Software: Cursor
# @Description: 用户管理API

from fastapi import APIRouter, Request

from src.core.responses.response import response_base
from src.database.db_session import async_audit_session, async_session

from ..model import User, user_schemas

router = APIRouter(prefix="/user", tags=["用户管理"])


@router.post("/create_user")
async def create_user(
    request: Request,
    user: user_schemas["Create"]  # type: ignore
):
    async with async_audit_session(async_session(), request) as session:
        data = await User.create(session=session, **user.model_dump())

    return response_base.success(data=data)

@router.get("/get_user")
async def get_user(
    user_id: int
):
    user = await User.get_by_id(user_id)
    if not user:
        return response_base.fail(data="用户不存在")
    return response_base.success(data=await user.to_dict())