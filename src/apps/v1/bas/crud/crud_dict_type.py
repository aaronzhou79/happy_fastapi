# src/apps/v1/bas/crud/crud_dict_type.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-19
# @Author  : lei
# @File    : crud_dict_type.py
# @Software: Cursor
# @Description: 字典类型CRUD类

from sqlmodel import select

from src.apps.v1.bas.models.mdl_dict_type import DictType, DictTypeCreate, DictTypeUpdate
from src.common.base_crud import CRUDBase
from src.database.db_session import AuditAsyncSession


class CrudDictType(CRUDBase):
    """字典类型CRUD类"""
    def __init__(self):
        super().__init__(
            model=DictType,
            create_model=DictTypeCreate,
            update_model=DictTypeUpdate,
        )

    async def get_dict_type(self, session: AuditAsyncSession, code: str, ignore_id: int = 0) -> DictType:
        """
        根据编码获取数据
        """
        query = select(self.model).where(self.model.code == code)

        if ignore_id > 0:
            query = query.where(self.model.id != ignore_id)

        result = await session.execute(query)

        return result.scalars().first()


crud_dict_type = CrudDictType()
