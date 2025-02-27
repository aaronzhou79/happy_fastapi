# src/apps/v1/sys/models/factory_user.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : factory_user.py
# @Software: Cursor
# @Description: 工厂用户API

from typing import Annotated

from fastapi import Body, Depends, Request

from src.apps.v1.sys.models.mdl_factory_user import FactoryUser, FactoryUserBase, FactoryUserCreate, FactoryUserUpdate
from src.apps.v1.sys.service.svr_factory_user import svr_factory_user
from src.common.base_api import BaseAPI
from src.core.responses.response_schema import ResponseModel, response_base
from src.core.security.auth_security import DependsJwtAuth
from src.core.security.permission import RequestPermission
from src.database.db_session import CurrentSession, async_audit_session, async_session

factory_user_api = BaseAPI(
    module_name="sys",
    model=FactoryUser,
    service=svr_factory_user,
    create_schema=FactoryUserCreate,
    update_schema=FactoryUserUpdate,
    base_schema=FactoryUserBase,
    prefix="/factory_user",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=["系统管理/工厂用户"],
)


@factory_user_api.router.get("/get_by_factory_id",
    description="获取工厂用户",
    dependencies=[
        DependsJwtAuth,
    ])
async def get_by_factory_id(session: CurrentSession,
                            factory_id: int, is_factory_user: bool) -> ResponseModel:
    """
    获取工厂用户

    :param factory_id: 工厂id
    :param is_factory_user: 是否当前工厂用户
    """
    data = await svr_factory_user.get_by_factory_id(session, factory_id, is_factory_user)

    return response_base.success(data=data)


@factory_user_api.router.get("/get_by_user_id",
    description="获取用户工厂",
    dependencies=[
        DependsJwtAuth,
    ])
async def get_by_user_id(session: CurrentSession, user_id: int) -> ResponseModel:
    """
    获取用户工厂

    :param user_id: 用户id
    """
    data = await svr_factory_user.get_by_user_id(session, user_id)

    return response_base.success(data=data)


@factory_user_api.router.post(
    "/clear_factory_users",
    description="清除工厂用户, 权限码：sys:factory_users:clear_factory_users",
    dependencies=[
        DependsJwtAuth,
        Depends(RequestPermission("sys:factory_users:clear_factory_users"))
    ]
)
async def clear_factory_users(
    request: Request,
    factory_id: Annotated[int, Body(..., description="工厂ID")],
    user_ids: Annotated[list[int], Body(..., description="用户ID列表")] = None,
) -> ResponseModel:
    """清除工厂用户"""
    async with async_audit_session(async_session(), request) as session:
        await svr_factory_user.clear_factory_users(session, factory_id, user_ids)
    return response_base.success(data={"message": "清除工厂用户成功"})
