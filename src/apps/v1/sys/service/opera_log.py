# src/apps/v1/sys/service/svr_opera_log.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : svr_opera_log.py
# @Software: Cursor
# @Description: 操作日志服务

from src.apps.v1.sys.crud.opera_log import crud_opera_log
from src.apps.v1.sys.models.opera_log import OperaLog, OperaLogCreate, OperaLogUpdate
from src.common.base_service import BaseService
from src.database.db_session import async_audit_session, async_session


class SvrOperaLog(BaseService[OperaLog, OperaLogCreate, OperaLogUpdate]):  # type: ignore
    """
    操作日志服务
    """
    def __init__(self):
        self.crud = crud_opera_log

    async def create_opera_log(self, opera_log_in: OperaLogCreate) -> dict:  # type: ignore
        """
        创建操作日志
        """
        async with async_audit_session(async_session()) as session:
            return await self.crud.create(session=session, obj_in=opera_log_in)


svr_opera_log = SvrOperaLog()
