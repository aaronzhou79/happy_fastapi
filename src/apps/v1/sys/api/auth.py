# src/apps/v1/sys/api/auth.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : auth.py
# @Software: Cursor
# @Description: 用户认证API
from fastapi import APIRouter, BackgroundTasks, Request, Response

from src.apps.v1.sys.models import AuthLoginParam
from src.apps.v1.sys.service.svr_auth import AuthService
from src.core.responses.response_schema import ResponseModel, response_base

"""
用户认证API
"""
router = APIRouter(prefix="/auth", tags=["用户认证"])


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    obj: AuthLoginParam,
    background_tasks: BackgroundTasks,
) -> ResponseModel:
    """
    用户登录

    :param obj: 用户名密码
    :return: 登录成功后的token
    """
    data = await AuthService.login(request=request, response=response, obj=obj, background_tasks=background_tasks)
    return response_base.success(data=data)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
) -> ResponseModel:
    """用户登出"""
    data = await AuthService.logout(request=request, response=response)
    return response_base.success(data=data)

