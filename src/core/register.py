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

from src.apps import router as apps_router
from src.common.data_model.base_model import create_table
from src.core.conf import settings
from src.core.exceptions.exception_handlers import register_exception
from src.core.responses.response_code import MsgSpecJSONResponse


@asynccontextmanager
async def register_init(app: FastAPI):
    await create_table()

    yield


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

