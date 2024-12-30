# src/apps/v1/sys/__init__.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Data    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : __init__.py
# @Software: Cursor
# @Description: 系统管理模块

from fastapi import APIRouter

from .api.dept import router as dept_router
from .api.user import router as user_router

router = APIRouter(prefix="/sys", tags=["系统管理"])

router.include_router(dept_router)
router.include_router(user_router)
