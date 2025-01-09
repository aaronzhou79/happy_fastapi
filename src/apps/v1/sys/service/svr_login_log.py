# src/apps/v1/sys/service/svr_login_log.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : svr_login_log.py
# @Software: Cursor
# @Description: 登录日志服务

from src.apps.v1.sys.crud.login_log import crud_login_log
from src.apps.v1.sys.models.login_log import LoginLog, LoginLogCreate, LoginLogUpdate
from src.common.base_service import BaseService
from src.database.db_session import AuditAsyncSession


class SvrLoginLog(BaseService[LoginLog, LoginLogCreate, LoginLogUpdate]):
    """
    登录日志服务
    """
    @staticmethod
    async def create_login_log(session: AuditAsyncSession, login_log_in: LoginLogCreate) -> dict:  # type: ignore
        """
        创建登录日志
        """
        return await crud_login_log.create(session=session, obj_in=login_log_in)


svr_login_log = SvrLoginLog(crud=crud_login_log)
