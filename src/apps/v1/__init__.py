# src/apps/v1/__init__.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/27 17:19
# @Author  : Aaron Zhou
# @File    : __init__.py
# @Software: Cursor
# @Description: apps/v1/ 总路由

from fastapi import APIRouter  # noqa: I001

from .init_data.api import router as init_data_router
from .sys import router as sys_router
from .bas import router as bas_router

router = APIRouter(prefix="/v1")

# router.include_router(code_gen_router)
router.include_router(bas_router)
router.include_router(sys_router)
router.include_router(init_data_router)