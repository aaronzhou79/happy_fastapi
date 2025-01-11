# src/apps/v1/sys/crud/login_log.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : login_log.py
# @Software: Cursor
# @Description: 登录日志相关CRUD类
from src.apps.v1.sys.models.login_log import LoginLog, LoginLogCreate, LoginLogUpdate
from src.common.base_crud import CRUDBase


class CrudLoginLog(CRUDBase):
    """登录日志相关CRUD类"""
    def __init__(self):
        super().__init__(
            model=LoginLog,
            create_model=LoginLogCreate,
            update_model=LoginLogUpdate,
        )


crud_login_log = CrudLoginLog()
