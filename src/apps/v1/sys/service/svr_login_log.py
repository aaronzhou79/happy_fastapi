# src/apps/v1/sys/service/svr_login_log.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : svr_login_log.py
# @Software: Cursor
# @Description: 登录日志服务

from fastapi import Request
from src.apps.v1.sys.crud.crud_login_log import crud_login_log
from src.apps.v1.sys.models.mdl_login_log import (
    LoginLog,
    LoginLogCreate,
    LoginLogUpdate,
)
from src.common.base_service import BaseService
from src.database.db_session import (
    AuditAsyncSession,
    async_audit_session,
    async_session,
)


class SvrLoginLog(BaseService[LoginLog, LoginLogCreate, LoginLogUpdate]):
    """
    登录日志服务
    """

    def __init__(self):
        self.crud = crud_login_log

    async def create_login_log(
        self, request: Request, login_log_in: LoginLogCreate
    ) -> LoginLog:
        """
        创建登录日志
        """
        # 后台任务，需要自己处理数据库会话，不能传入主程的session
        async with async_audit_session(async_session(), request=request) as session:
            return await self.crud.create(session=session, obj_in=login_log_in)


svr_login_log = SvrLoginLog()
