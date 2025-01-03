# src/core/register.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/27 17:19
# @Author  : Aaron Zhou
# @File    : register.py
# @Software: Cursor
# @Description: 应用注册初始化

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter

from src.apps import router as apps_router
from src.common.data_model.base_model import create_table
from src.core.conf import settings
from src.core.exceptions.exception_handlers import register_exception
from src.core.responses.response_code import MsgSpecJSONResponse
from src.database.db_redis import redis_client
from src.utils.health_check import http_limit_callback


@asynccontextmanager
async def register_init(app: FastAPI):
    try:
        # # 初始化 Redis
        await redis_client.open()
        await create_table()
        # 初始化限流器
        await FastAPILimiter.init(
            redis=redis_client.client,
            prefix=settings.REQUEST_LIMITER_REDIS_PREFIX or 'fastapi_limiter',
            http_callback=http_limit_callback,
        )

        yield
    finally:
        await FastAPILimiter.close()
        await redis_client.client.close()


def register_app():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
        openapi_url=settings.OPENAPI_URL,
        default_response_class=MsgSpecJSONResponse,
        lifespan=register_init,
    )

    app.include_router(apps_router)

    register_exception(app)

    return app

