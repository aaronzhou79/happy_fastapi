# src/apps/v1/__init__.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Data    : 2024/12/27 17:19
# @Author  : Aaron Zhou
# @File    : __init__.py
# @Software: Cursor
# @Description: apps/v1/ 总路由

from fastapi import APIRouter

from .demo_code import router as demo_code_router

router = APIRouter(prefix="/v1")

router.include_router(demo_code_router)
