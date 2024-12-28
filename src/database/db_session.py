# src/database/db_session.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/28
# @Author  : Aaron Zhou
# @File    : db_session.py
# @Software: Cursor
# @Description: 数据库会话管理

import asyncio

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.conf import settings


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session
