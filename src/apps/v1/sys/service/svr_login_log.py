# src/apps/v1/sys/service/svr_login_log.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : svr_login_log.py
# @Software: Cursor
# @Description: 登录日志服务

from src.apps.v1.sys.models import LoginLog, LoginLogSchemaCreate
from src.database.db_session import AuditAsyncSession


class SvrLoginLog():
    """
    登录日志服务
    """
    @staticmethod
    async def create_login_log(session: AuditAsyncSession, login_log_in: LoginLogSchemaCreate) -> dict:  # type: ignore
        """
        创建登录日志
        """
        return await LoginLog.create(session, **login_log_in.model_dump())
