# src/apps/v1/sys/__init__.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : __init__.py
# @Software: Cursor
# @Description: 系统管理模块

from fastapi import APIRouter

from .api.audit_log import audit_log_api
from .api.dept import dept_api
from .api.user import user_api

router = APIRouter(prefix="/sys")

router.include_router(dept_api.router)
router.include_router(user_api.router)
router.include_router(audit_log_api.router)
