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

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.routing import APIRoute
from fastapi_limiter import FastAPILimiter
from starlette.middleware.authentication import AuthenticationMiddleware

from src.apps import router as apps_router
from src.common.base_model import create_table
from src.common.logger import log, set_customize_logfile, setup_logging
from src.core.conf import settings
from src.core.exceptions.exception_handler import register_exception
from src.core.responses.response_schema import MsgSpecJSONResponse
from src.database.db_redis import redis_client
from src.middleware.jwt_auth_middleware import JwtAuthMiddleware
from src.middleware.opera_log_middleware import OperaLogMiddleware
from src.middleware.profiling_middleware import ProfilingMiddleware
from src.middleware.state_middleware import StateMiddleware
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
    except Exception as e:
        log.error("❌ 注册初始化失败: {}", e)
        log.error("==请检查环境后重试！")
    finally:
        await close_limiter()
        await redis_client.close()


def register_app() -> FastAPI:
    """注册应用"""
    register_logger()

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

    register_middleware(app)

    register_routers(app)

    register_exception(app)

    return app


def register_routers(app: FastAPI) -> None:
    """注册路由"""

    def _generate_operation_id(route: APIRoute) -> str:
        """生成简化的operation_id

        去掉api/v1前缀,使用更简洁的格式: {module}_{resource}
        """
        # 获取路径中最后两段作为资源名
        path_parts = route.path.strip("/").replace("api/v1/", "").split("/")
        resource = "_".join(path_parts)

        return f"{resource}"

    app.router.generate_unique_id_function = _generate_operation_id
    app.include_router(apps_router)


def register_middleware(app: FastAPI) -> None:
    """
    中间件，执行顺序从下往上

    :param app:
    :return:
    """
    # GZip
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    # State (required)
    app.add_middleware(StateMiddleware)
    # Opera log (required)
    app.add_middleware(OperaLogMiddleware)
    # JWT auth (required)
    app.add_middleware(
        AuthenticationMiddleware,
        backend=JwtAuthMiddleware(),
        on_error=JwtAuthMiddleware.auth_exception_handler,  # type: ignore
    )
    # Trace ID (required)
    app.add_middleware(CorrelationIdMiddleware, validator=None)
    # Profiling (optional)
    if settings.APP_DEBUG:
        app.add_middleware(ProfilingMiddleware)

    # CORS: Always at the end
    if settings.MIDDLEWARE_CORS:
        from fastapi.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
            expose_headers=settings.CORS_EXPOSE_HEADERS,
        )


def register_logger() -> None:
    """
    注册系统日志管理模块
    """
    setup_logging()
    set_customize_logfile()