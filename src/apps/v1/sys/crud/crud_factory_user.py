# src/apps/v1/sys/models/factory_user.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : factory_user.py
# @Software: Cursor
# @Description: 工厂用户CRUD类

from typing import Sequence

from sqlalchemy import delete
from sqlmodel import select

from src.apps.v1.sys.models.mdl_factory_user import FactoryUser, FactoryUserCreate, FactoryUserUpdate
from src.common.base_crud import CRUDBase
from src.database.db_session import AuditAsyncSession


class CrudFactoryUser(CRUDBase):
    """工厂用户CRUD类"""
    def __init__(self):
        super().__init__(
            model=FactoryUser,
            create_model=FactoryUserCreate,
            update_model=FactoryUserUpdate,
        )

    async def clear_factory_users(self, session: AuditAsyncSession, factory_id: int, user_ids: list[int]) -> None:
        """
        清除工厂用户

        :param factory_id: 工厂id
        :param user_ids: 用户id数组
        """
        await session.execute(
            delete(self.model)
            .where(self.model.factory_id == factory_id)
            .where(self.model.user_id.in_(user_ids))
        )

        await session.flush()

    async def get_by_factory_id(self, session: AuditAsyncSession, factory_id: int) -> Sequence[FactoryUser]:
        """
        获取工厂用户

        :param factory_id: 工厂id
        """
        result = await session.execute(
            select(self.model).where(self.model.factory_id == factory_id)
        )

        return result.scalars().all()

    async def get_by_user_id(self, session: AuditAsyncSession, user_id: int) -> Sequence[FactoryUser]:
        """
        获取用户工厂

        :param user_id: 用户id
        """
        result = await session.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return result.scalars().all()


crud_factory_user = CrudFactoryUser()
