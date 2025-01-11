# src/apps/v1/sys/__init__.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : __init__.py
# @Software: Cursor
# @Description: 系统管理模块

from fastapi import APIRouter

from .api.auth import router as auth_api
from .api.dept import dept_api
from .api.login_log import login_log_api
from .api.opera_log import opera_log_api
from .api.permission import permission_api
from .api.permission_rule import permission_rule_api
from .api.role import role_api
from .api.user import user_api

router = APIRouter(prefix="/sys")

router.include_router(auth_api)
router.include_router(dept_api.router)
router.include_router(role_api.router)
router.include_router(user_api.router)
router.include_router(opera_log_api.router)
router.include_router(login_log_api.router)
router.include_router(permission_api.router)
router.include_router(permission_rule_api.router)