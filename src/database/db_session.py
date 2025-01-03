# src/database/db_session.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/28
# @Author  : Aaron Zhou
# @File    : db_session.py
# @Software: Cursor
# @Description: 数据库会话管理
import asyncio

from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator
from uuid import uuid4

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, async_sessionmaker, create_async_engine

from src.core.conf import settings

if settings.DB_TYPE == 'sqlite':
    SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///./{settings.DB_NAME}"
elif settings.DB_TYPE == 'mysql':
    SQLALCHEMY_DATABASE_URL = f"mysql+aiomysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
elif settings.DB_TYPE == 'postgresql':
    SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
elif settings.DB_TYPE == 'dm':
    SQLALCHEMY_DATABASE_URL = f"dm+dmPython://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
elif settings.DB_TYPE == 'kingbase':
    SQLALCHEMY_DATABASE_URL = f"kingbase+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
elif settings.DB_TYPE == 'oscar':
    SQLALCHEMY_DATABASE_URL = f"oscar+pyodbc://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
elif settings.DB_TYPE == 'gbase':
    SQLALCHEMY_DATABASE_URL = f"gbase+pygbase://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
else:
    raise ValueError(f"Invalid database type: {settings.DB_TYPE}")


class AuditAsyncSession(AsyncSession):
    """扩展AsyncSession以支持审计"""
    _user_id: int | None = None

    @property
    def user_id(self) -> int | None:
        return self._user_id

    @user_id.setter
    def user_id(self, value: int | None) -> None:
        self._user_id = value


async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=settings.APP_DEBUG,
    pool_pre_ping=True,
) if settings.DB_TYPE == 'sqlite' else create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=settings.APP_DEBUG,
    pool_recycle=3600,
    pool_size=20,
    max_overflow=10,
)

async_session = async_sessionmaker(
    async_engine,
    class_=AuditAsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@asynccontextmanager
async def async_audit_session(
    session: AuditAsyncSession,
    request: Request | None = None,
) -> AsyncGenerator[AuditAsyncSession, None]:
    """带审计功能的会话上下文管理器"""
    try:
        if request and hasattr(request, 'user_id'):
            session.user_id = getattr(request, "user_id", None)

        yield session

        await session.commit()

    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


AsyncSessionScoped = async_scoped_session(async_session, scopefunc=asyncio.current_task)


async def get_db():
    async with AsyncSessionScoped() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


CurrentSession = Annotated[AuditAsyncSession, Depends(get_db)]


def uuid4_str() -> str:
    """数据库引擎 UUID 类型兼容性解决方案"""
    return str(uuid4())