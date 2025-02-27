# src/apps/v1/bas/service/svr_dict_data.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-19
# @Author  : lei
# @File    : svr_dict_data.py
# @Software: Cursor
# @Description: 字典数据服务

from typing import Sequence

from src.apps.v1.bas.crud.crud_dict_data import crud_dict_data
from src.apps.v1.bas.models.mdl_dict_data import DictData, DictDataCreate, DictDataUpdate
from src.common.base_crud import HookContext
from src.common.base_service import BaseService
from src.common.enums import HookTypeEnum
from src.core.exceptions import errors
from src.database.db_session import AuditAsyncSession


class SvrDictData(BaseService[DictData, DictDataCreate, DictDataUpdate]):
    """
    字典数据服务
    """
    def __init__(self):
        self.crud = crud_dict_data

    async def get_dict_datas(self, session: AuditAsyncSession, dict_code: str) -> Sequence[DictData]:
        """
        根据字典类型编码获取字典值

        :param dict_code: 字典类型编码
        :return: 字典值
        """
        return await self.crud.get_dict_datas(session, dict_code)


svr_dict_data = SvrDictData()
