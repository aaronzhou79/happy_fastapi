# src/apps/v1/demo_code/__init__.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Data    : 2024/12/27 17:20
# @Author  : Aaron Zhou
# @File    : __init__.py
# @Software: Cursor
# @Description: apps/v1/demo_code/ 路由

from fastapi import APIRouter

from .api import router as api_router

router = APIRouter(prefix="/demo_code")

router.include_router(api_router)
