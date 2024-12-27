# src/core/register.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Data    : 2024/12/27 17:19
# @Author  : Aaron Zhou
# @File    : register.py
# @Software: Cursor
# @Description: 应用注册初始化

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from src.apps import router as apps_router
from src.core.conf import settings
from src.core.exceptions.custom_exceptions import CustomException
from src.core.exceptions.exception_handlers import GlobalExceptionHandler, register_exception
from src.core.responses.response_code import MsgSpecJSONResponse, ResponseCode, ResponseMessage


@asynccontextmanager
async def register_init(app: FastAPI):
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

    app.include_router(apps_router, prefix="/api")

    register_exception(app)

    return app

