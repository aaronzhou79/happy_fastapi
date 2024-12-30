# src/apps/v1/demo_code/__init__.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/27 17:20
# @Author  : Aaron Zhou
# @File    : __init__.py
# @Software: Cursor
# @Description: apps/v1/demo_code/ 路由

from fastapi import APIRouter

from .api import article_api, comment_api

router = APIRouter(prefix="/demo_code")

router.include_router(article_api.router)
router.include_router(comment_api.router)
