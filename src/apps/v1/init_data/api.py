# src/apps/v1/init_data/api.py
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024/12/29
# @Author  : Aaron Zhou
# @File    : api.py
# @Software: Cursor
# @Description: 数据初始化API
from fastapi import APIRouter, Response

from src.apps.v1.init_data import init_data
from src.core.responses.response_schema import response_base

router = APIRouter()


@router.post('/init_data')
async def initdata() -> Response:
    """初始化数据"""
    await init_data()
    return response_base.fast_success(data='数据初始化成功')
