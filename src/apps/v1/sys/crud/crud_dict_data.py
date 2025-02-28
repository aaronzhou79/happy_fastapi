# src/apps/v1/bas/crud/crud_dict_data.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-19
# @Author  : lei
# @File    : crud_dict_data.py
# @Software: Cursor
# @Description: 字典数据CRUD类

from typing import Sequence

from sqlmodel import select

from src.apps.v1.bas.models.mdl_dict_data import DictData, DictDataCreate, DictDataUpdate
from src.common.base_crud import CRUDBase
from src.database.db_session import AuditAsyncSession


class CrudDictData(CRUDBase):
    """字典数据CRUD类"""
    def __init__(self):
        super().__init__(
            model=DictData,
            create_model=DictDataCreate,
            update_model=DictDataUpdate,
        )

    async def get_dict_datas(self, session: AuditAsyncSession, dict_code: str) -> Sequence[DictData]:
        """
        根据字典类型编码获取字典值

        :param dict_code: 字典类型编码
        :return: 字典值
        """
        result = await session.execute(
            select(self.model)
            .where(self.model.code == dict_code)
        )

        return result.scalars()._allrows()


crud_dict_data = CrudDictData()
