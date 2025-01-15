# src/apps/v1/sys/api/user.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : user.py
# @Software: Cursor
# @Description: 用户管理API
from typing import Annotated

from fastapi import BackgroundTasks, Body, Depends, Request, Response

from src.apps.v1.sys.models.user import (
    AuthLoginParam,
    GetLoginToken,
    User,
    UserCreateWithRoles,
    UserGetWithRoles,
    UserUpdate,
)
from src.apps.v1.sys.service.auth import svr_auth
from src.apps.v1.sys.service.user import svr_user
from src.common.base_api import BaseAPI
from src.core.responses.response_schema import ResponseModel, response_base
from src.core.security.auth_security import DependsJwtAuth
from src.core.security.permission import RequestPermission

user_api = BaseAPI(
    module_name="sys",
    model=User,
    service=svr_user,
    create_schema=UserCreateWithRoles,
    update_schema=UserUpdate,
    base_schema=UserGetWithRoles,
    prefix="/user",
    gen_delete=True,
    tags=["系统管理/用户管理"],
)

@user_api.router.post("/login")
async def login(
    request: Request,
    response: Response,
    obj: AuthLoginParam,
    background_tasks: BackgroundTasks,
) -> ResponseModel[GetLoginToken]:
    """
    用户登录

    :param obj: 用户名密码
    :return: 登录成功后的token
    """
    data = await svr_auth.login(request=request, response=response, obj=obj, background_tasks=background_tasks)
    return response_base.success(data=data)


@user_api.router.post(
    "/logout",
    dependencies=[
        DependsJwtAuth,
    ]
)
async def logout(
    request: Request,
    response: Response,
) -> ResponseModel:
    """用户登出"""
    data = await svr_auth.logout(request=request, response=response)
    return response_base.success(data=data)


@user_api.router.post(
    "/set_as_user",
    description="设置用户, 权限码：sys:auth:set_as_user",
    dependencies=[
        DependsJwtAuth,
        Depends(RequestPermission("sys:auth:set_as_user"))
    ]
)
async def set_as_user(
    request: Request,
    id: Annotated[int, Body(..., description="员工ID")],
    username: Annotated[str, Body(..., description="用户名")],
    password: Annotated[str, Body(..., description="登录密码")],
    roles: Annotated[list[int] | None, Body(..., description="角色ID列表")] = None,
) -> ResponseModel:
    """设置为用户"""
    data = await svr_auth.set_as_user(request=request, id=id, username=username, password=password, roles=roles)
    return response_base.success(data=data)


@user_api.router.get("/me",
    dependencies=[
        DependsJwtAuth,
    ])
async def me(request: Request) -> ResponseModel:
    """获取当前用户信息"""
    data = UserGetWithRoles.model_validate(request.user.user_data.model_dump())
    return response_base.success(data=data)

