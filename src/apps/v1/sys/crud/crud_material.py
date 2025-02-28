# src/apps/v1/bas/crud/crud_material.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : crud_material.py
# @Software: Cursor
# @Description: 物料信息CRUD类

from sqlmodel import select

from src.apps.v1.bas.models.mdl_material import Material, MaterialCreate, MaterialUpdate
from src.common.base_crud import CRUDBase
from src.database.db_session import AuditAsyncSession


class CrudMaterial(CRUDBase):
    """物料信息CRUD类"""
    def __init__(self):
        super().__init__(
            model=Material,
            create_model=MaterialCreate,
            update_model=MaterialUpdate,
        )

    async def get_material(self, session: AuditAsyncSession, material_code: str, material_id: int = 0) -> Material:
        """
        获取相同编码物料

        :param material_code: 物料编码
        :param material_id: 物料id
        :return: 相同编码的物料
        """
        result = await session.execute(
            select(self.model)
            .where(self.model.code == material_code)
            .where(self.model.id != material_id)
        )

        return result.scalars().first()


crud_material = CrudMaterial()
