# src/apps/v1/init_data/api.py
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2024/12/29
# @Author  : Aaron Zhou
# @File    : api.py
# @Software: Cursor
# @Description: 数据初始化API

from fastapi import APIRouter

from src.apps.v1.init_data import init_data
from src.core.responses.response import response_base

router = APIRouter()


@router.post('/init')
async def init():
    await init_data()
    return response_base.fast_success(data='数据初始化成功')
