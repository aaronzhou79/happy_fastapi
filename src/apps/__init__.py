# src/apps/__init__.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/27 17:18
# @Author  : Aaron Zhou
# @File    : __init__.py
# @Software: Cursor
# @Description: apps 总路由

from fastapi import APIRouter

from src.core.conf import settings

from .v1 import router as v1_router

router = APIRouter(prefix=settings.API_PATH)

router.include_router(v1_router)
