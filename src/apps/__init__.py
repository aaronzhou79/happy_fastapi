# src/apps/__init__.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/27 17:18
# @Author  : Aaron Zhou
# @File    : __init__.py
# @Software: Cursor
# @Description: apps 总路由

from fastapi import APIRouter

from .v1 import router as v1_router

router = APIRouter()

router.include_router(v1_router)
