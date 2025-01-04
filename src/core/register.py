# src/core/register.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/27 17:19
# @Author  : Aaron Zhou
# @File    : register.py
# @Software: Cursor
# @Description: 应用注册初始化

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter

from src.apps import router as apps_router
from src.common.data_model.base_model import create_table
from src.common.logger import log
from src.core.conf import settings
from src.core.exceptions.exception_handlers import register_exception
from src.core.responses.response_code import MsgSpecJSONResponse
from src.database.db_redis import redis_client
from src.utils.health_check import http_limit_callback


async def init_limiter() -> None:
    """初始化限流器"""
    try:

        await FastAPILimiter.init(
            redis=redis_client,
            prefix=settings.REQUEST_LIMITER_REDIS_PREFIX or 'fastapi_limiter',
            http_callback=http_limit_callback,
        )
        log.info("🟢 限流器初始化成功")
    except Exception as e:
        log.error("❌ 限流器初始化失败: {}", e)
        # 这里可以选择是否退出程序
        # sys.exit(1)


async def close_limiter() -> None:
    """关闭限流器"""
    try:
        if FastAPILimiter.redis:  # 检查redis实例是否存在
            await FastAPILimiter.close()
            log.info("🟢 限流器关闭成功")
    except Exception as e:
        log.error("❌ 限流器关闭失败: {}", e)


@asynccontextmanager
async def register_init(app: FastAPI) -> AsyncIterator[None]:
    """注册初始化"""
    try:
        # # 初始化 Redis
        await redis_client.open()
        await create_table()
        # 初始化限流器
        await init_limiter()

        yield
    finally:
        await close_limiter()
        await redis_client.close()


def register_app() -> FastAPI:
    """注册应用"""
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

