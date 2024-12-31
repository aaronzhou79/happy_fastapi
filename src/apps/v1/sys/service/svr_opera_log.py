# src/apps/v1/sys/service/svr_opera_log.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : svr_opera_log.py
# @Software: Cursor
# @Description: 操作日志服务

from typing import TYPE_CHECKING

from src.apps.v1.sys.model.opera_log import OperaLog
from src.database.db_session import async_audit_session, async_session

if TYPE_CHECKING:
    from src.apps.v1.sys.model.opera_log import OperaLogCreate


class SvrOperaLog:
    @staticmethod
    async def create_opera_log(opera_log_in: "OperaLogCreate") -> dict:
        async with async_audit_session(async_session()) as session:
            return await OperaLog.create(session, **opera_log_in.model_dump())
