# src/apps/v1/sys/crud/opera_log.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/31
# @Author  : Aaron Zhou
# @File    : opera_log.py
# @Software: Cursor
# @Description: 操作日志相关CRUD类
from src.apps.v1.sys.models.opera_log import OperaLog, OperaLogCreate, OperaLogUpdate
from src.common.base_crud import CRUDBase


class CrudOperaLog(CRUDBase):
    """操作日志相关CRUD类"""


crud_opera_log = CrudOperaLog(OperaLog, OperaLogCreate, OperaLogUpdate)
