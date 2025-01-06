# src/apps/v1/sys/service/svr_opera_log.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : svr_opera_log.py
# @Software: Cursor
# @Description: 操作日志服务
from src.apps.v1.sys.models import OperaLog, OperaLogSchemaCreate
from src.common.logger import log
from src.core.conf import settings
from src.database.db_session import async_audit_session, async_session


class SvrOperaLog:
    """
    操作日志服务
    """
    @staticmethod
    async def create_opera_log(opera_log_in: OperaLogSchemaCreate) -> dict:  # type: ignore
        """
        创建操作日志
        """
        if settings.APP_DEBUG:
            log.info("================================================")
            log.info(opera_log_in.model_dump())
        async with async_audit_session(async_session()) as session:
            return await OperaLog.create(session, **opera_log_in.model_dump())